from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import login
from django.views.generic import TemplateView
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden, JsonResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Product, Category, Cart, CartItem, Order, OrderItem, Promotion, Review, OrderStatusLog, User
from .forms import ProductForm, CategoryForm, UserRegistrationForm, UserProfileForm, OrderForm, ReviewForm

def group_required(*group_names):
    def in_groups(u):
        if u.is_authenticated:
            if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
                return True
        return False
    return user_passes_test(in_groups)

class APIDocsView(TemplateView):
    template_name = 'shopapp/api_docs.html'

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    featured_products = Product.objects.filter(is_featured=True, available=True)[:4]
    
    if len(featured_products) < 4:
        additional_products = Product.objects.filter(available=True).exclude(id__in=[p.id for p in featured_products])[:4-len(featured_products)]
        featured_products = list(featured_products) + list(additional_products)
    
    context = {
        'category': category,
        'categories': categories,
        'products': products,
        'featured_products': featured_products,
    }
    
    return render(request, 'shopapp/index.html', context)

@login_required
def product_detail(request, id):
    product = get_object_or_404(Product, id=id, available=True)
    reviews = product.reviews.filter(is_approved=True, parent__isnull=True)
    review_form = ReviewForm()
    average_rating = Review.get_average_rating(product.id)
    
    can_review = False
    if request.user.is_authenticated:
        can_review = OrderItem.objects.filter(
            order__user=request.user,
            product=product
        ).exists()
    
    return render(request, 'shopapp/product/detail.html', {
        'product': product,
        'reviews': reviews,
        'review_form': review_form,
        'average_rating': average_rating,
        'can_review': can_review,
    })

def catalog(request, category_id=None):
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    current_category = None
    if category_id:
        current_category = get_object_or_404(Category, id=category_id)
        products = products.filter(category=current_category)
    
    product_type = request.GET.get('type')
    if product_type and product_type != 'all':
        products = products.filter(category_type=product_type)
    
    sort = request.GET.get('sort', '')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created')
    else:
        products = products.order_by('name')
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    context = {
        'current_category': current_category,
        'categories': categories,
        'page_obj': page_obj,
        'current_type': product_type,
    }
    
    return render(request, 'shopapp/catalog.html', context)

@login_required
@group_required('Seller', 'Admin', 'Superuser')
@permission_required('shopapp.add_product', raise_exception=True)
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Товар успешно создан')
            return redirect('shopapp:catalog')
    else:
        form = ProductForm()
    
    return render(request, 'shopapp/admin/product_form.html', {
        'form': form,
        'title': 'Добавить товар'
    })

@login_required
@permission_required('shopapp.change_product', raise_exception=True)
def product_edit(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Товар успешно обновлен')
            return redirect(product.get_absolute_url())
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'shopapp/admin/product_form.html', {
        'form': form,
        'title': 'Редактировать товар',
        'product': product
    })

@login_required
@permission_required('shopapp.delete_product', raise_exception=True)
def product_delete(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Товар успешно удален')
        return redirect('shopapp:catalog')
    
    return render(request, 'shopapp/admin/product_confirm_delete.html', {
        'product': product
    })

@login_required
@group_required('Admin', 'Superuser')
@permission_required('shopapp.add_category', raise_exception=True)
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Категория успешно создана')
            return redirect('shopapp:catalog')
    else:
        form = CategoryForm()
    
    return render(request, 'shopapp/admin/category_form.html', {
        'title': 'Добавить категорию',
        'form': form
    })

@login_required
@permission_required('shopapp.change_category', raise_exception=True)
def category_edit(request, id):
    category = get_object_or_404(Category, id=id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Категория успешно обновлена')
            return redirect('shopapp:catalog')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'shopapp/admin/category_form.html', {
        'title': 'Редактировать категорию',
        'form': form,
        'category': category
    })

@login_required
@permission_required('shopapp.delete_category', raise_exception=True)
def category_delete(request, id):
    category = get_object_or_404(Category, id=id)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Категория успешно удалена')
        return redirect('shopapp:catalog')
    
    return render(request, 'shopapp/admin/category_confirm_delete.html', {
        'category': category
    })

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('shopapp:profile')
    else:
        form = UserRegistrationForm()
    return render(request, 'shopapp/auth/register.html', {'form': form})

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'shopapp/cart/cart.html', {'cart': cart})

@login_required
def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    return redirect('shopapp:cart_view')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('shopapp:cart_view')

@login_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
    return redirect('shopapp:cart_view')

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shopapp/order/detail.html', {'order': order})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shopapp/order/history.html', {'orders': orders})

@login_required
def profile(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')[:5]
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен')
            return redirect('shopapp:profile')
    else:
        form = UserProfileForm(instance=user)
    
    return render(request, 'shopapp/auth/profile.html', {
        'form': form,
        'orders': orders,
        'active_tab': 'profile'
    })

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total = sum(item.get_total_price() for item in cart.items.all())
            order.save()
            
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=item.product.price,
                    quantity=item.quantity
                )
            
            cart.items.all().delete()
            
            messages.success(request, f'Заказ #{order.order_number} успешно оформлен!')
            return redirect('shopapp:order_detail', order_id=order.id)
    else:
        initial_data = {
            'full_name': f"{request.user.first_name} {request.user.last_name}",
            'phone': request.user.phone_number,
            'delivery_address': request.user.address,
        }
        form = OrderForm(initial=initial_data)
    
    return render(request, 'shopapp/order/checkout.html', {
        'cart': cart,
        'form': form,
    })

def promotions(request):
    current_promotions = Promotion.objects.filter(is_active=True).order_by('-start_date')
    
    from django.utils import timezone
    now = timezone.now().date()
    
    active_promotions = []
    archive_promotions = []
    
    for promo in current_promotions:
        if promo.end_date and promo.end_date < now:
            archive_promotions.append(promo)
        else:
            active_promotions.append(promo)
    
    context = {
        'active_promotions': active_promotions,
        'archive_promotions': archive_promotions[:3],
    }
    
    return render(request, 'shopapp/promotions.html', context)

def about(request):
    return render(request, 'shopapp/about.html')

def subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        send_mail(
            'Подписка на рассылку',
            'Вы успешно подписались на рассылку акций нашего магазина.',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        
        messages.success(request, 'Вы успешно подписались на рассылку!')
        return redirect('shopapp:promotions')
    
    return redirect('shopapp:promotions')

@login_required
@require_POST
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Проверяем, покупал ли пользователь этот товар
    has_ordered = OrderItem.objects.filter(
        order__user=request.user,
        product=product
    ).exists()
    
    if not has_ordered and not request.user.is_staff:
        messages.error(request, 'Вы можете оставить отзыв только на купленные товары')
        return redirect(product.get_absolute_url())
    
    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.user = request.user
        
        # Автоматически одобряем отзывы от администраторов
        if request.user.has_perm('shopapp.can_approve_review'):
            review.is_approved = True
            messages.success(request, 'Ваш отзыв опубликован')
        else:
            messages.success(request, 'Ваш отзыв отправлен на модерацию')
        
        review.save()
        
        # Отправляем уведомление администраторам
        if not review.is_approved:
            send_review_moderation_email(review)
        
        return redirect('shopapp:product_detail', id=review.product.pk)
    
    messages.error(request, 'Ошибка при отправке отзыва')
    return redirect(product.get_absolute_url())

def send_review_moderation_email(review):
    admin_emails = User.objects.filter(
        groups__name__in=['Admin', 'Moderator']
    ).values_list('email', flat=True)
    
    if admin_emails:
        subject = f'Новый отзыв на модерацию: {review.product.name}'
        message = render_to_string('emails/review_moderation.html', {
            'review': review,
            'product': review.product,
            'admin_url': settings.ADMIN_URL,
        })
        plain_message = strip_tags(message)
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            admin_emails,
            html_message=message,
        )

@login_required
@require_POST
def add_review_reply(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    if not request.user.has_perm('shopapp.can_approve_review'):
        return HttpResponseForbidden()
    
    reply_text = request.POST.get('reply', '').strip()
    if reply_text:
        reply = Review.objects.create(
            product=review.product,
            user=request.user,
            text=reply_text,
            rating=0,
            is_approved=True,
            parent=review
        )
        messages.success(request, 'Ответ добавлен')
        
        send_mail(
            'Ответ на ваш отзыв',
            f'Магазин ответил на ваш отзыв к товару {review.product.name}:\n\n{reply_text}',
            settings.DEFAULT_FROM_EMAIL,
            [review.user.email],
        )
    
    return redirect(review.get_absolute_url())

@login_required
@group_required('Admin', 'Moderator')
def review_moderation(request):
    pending_reviews = Review.objects.filter(is_approved=False).order_by('-created_at')
    return render(request, 'shopapp/reviews/moderation.html', {
        'pending_reviews': pending_reviews
    })

@login_required
@group_required('Admin', 'Moderator')
@require_POST
@permission_required('shopapp.moderate_review')
def approve_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.is_approved = True
    review.is_rejected = False
    review.save()
    messages.success(request, 'Отзыв одобрен')
    return redirect('shopapp:review_moderation')

def send_review_approved_email(review):
    subject = f'Ваш отзыв на товар {review.product.name} был одобрен'
    message = render_to_string('review_approved.html', {
        'review': review,
        'product': review.product,
    })
    plain_message = strip_tags(message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [review.user.email],
        html_message=message,
    )

@login_required
@group_required('Admin', 'Moderator')
@require_POST
@permission_required('shopapp.moderate_review')
def reject_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.is_approved = False
    review.is_rejected = True
    review.save()
    messages.success(request, 'Отзыв отклонен')
    return redirect('shopapp:review_moderation') 

def send_review_rejected_email(user_email, product):
    subject = f'Ваш отзыв на товар {product.name} был отклонен'
    message = render_to_string('review_rejected.html', {
        'product': product,
    })
    plain_message = strip_tags(message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        html_message=message,
    )