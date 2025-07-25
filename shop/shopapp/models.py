from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.urls import reverse
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save, post_delete
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    # Добавляем related_name для разрешения конфликта
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='shopapp_user_set',
        related_query_name='shopapp_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='shopapp_user_set',
        related_query_name='shopapp_user',
    )

    class Meta:
        db_table = 'shopapp_user' 

class Category(models.Model):
    name = models.CharField("Название", max_length=100, unique=True)
    description = models.TextField("Описание", blank=True)
    created = models.DateTimeField("Создан", auto_now_add=True)
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('shopapp:catalog_by_category', args=[self.id])

class Product(models.Model):
    PROTEIN = 'protein'
    CREATINE = 'creatine'
    AMINO = 'amino'
    OTHER = 'other'
    
    CATEGORY_TYPES = [
        (PROTEIN, 'Протеин'),
        (CREATINE, 'Креатин'),
        (AMINO, 'Аминокислоты'),
        (OTHER, 'Другое'),
    ]
    
    category = models.ForeignKey(Category, verbose_name="Категория", on_delete=models.CASCADE)
    category_type = models.CharField("Тип продукта", max_length=20, choices=CATEGORY_TYPES, default=PROTEIN)
    name = models.CharField("Название", max_length=200, unique=True)
    image = models.ImageField("Изображение", upload_to='products/%Y/%m/%d', blank=True)
    description = models.TextField("Описание", blank=True)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    available = models.BooleanField("В наличии", default=True)
    is_featured = models.BooleanField("Рекомендуемый", default=False)
    protein_per_serving = models.PositiveIntegerField("Белок на порцию (г)", default=0)
    servings = models.PositiveIntegerField("Количество порций", default=1)
    created = models.DateTimeField("Создан", auto_now_add=True)
    average_rating = models.DecimalField(
        "Средний рейтинг", 
        max_digits=3, 
        decimal_places=2, 
        default=0
    )
    
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
    
    def __str__(self):
        return self.name
    
    def total_protein(self):
        return self.protein_per_serving * self.servings
    total_protein.short_description = 'Всего белка'
    total_protein.admin_order_field = 'protein_per_serving'
    
    def get_absolute_url(self):
        return reverse('shopapp:product_detail', kwargs={'id': self.pk})

class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    def get_total_price(self):
        return self.product.price * self.quantity

class Order(models.Model):
    DELIVERY_CHOICES = [
        ('courier', 'Доставка курьером'),
        ('pickup', 'Самовывоз'),
    ]
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    order_number = models.CharField(max_length=20, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    delivery_address = models.TextField()
    phone = models.CharField(max_length=20)
    full_name = models.CharField(max_length=100)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_CHOICES)
    status_changed = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.order_number}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    
    def get_item_total(self):
        return self.price * self.quantity

class Promotion(models.Model):
    title = models.CharField("Название", max_length=200)
    description = models.TextField("Описание")
    image = models.ImageField("Изображение", upload_to='promotions/%Y/%m/%d')
    discount = models.CharField("Скидка", max_length=50, blank=True)
    start_date = models.DateField("Дата начала")
    end_date = models.DateField("Дата окончания", blank=True, null=True)
    is_active = models.BooleanField("Активная", default=True)
    products = models.ManyToManyField(Product, blank=True, verbose_name="Товары по акции")
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        verbose_name = "Акция"
        verbose_name_plural = "Акции"
        ordering = ['-start_date']

    def __str__(self):
        return self.title

    def is_current(self):
        from django.utils import timezone
        now = timezone.now().date()
        if self.end_date:
            return self.start_date <= now <= self.end_date
        return self.start_date <= now

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def save(self, *args, **kwargs):
        if settings.MODERATION_SETTINGS['AUTO_MODERATION']:
            self.moderate()
        super().save(*args, **kwargs)
    
    def moderate(self):
        """Автоматическая модерация отзыва"""
        from django.conf import settings
        
        # Автоматическое одобрение для персонала
        if settings.REVIEW_SETTINGS['AUTO_APPROVE_STAFF'] and self.user.is_staff:
            self.is_approved = True
            return
        
        # Проверка на запрещенные слова
        text_lower = self.text.lower()
        if any(word in text_lower for word in settings.MODERATION_SETTINGS['FORBIDDEN_WORDS']):
            self.is_rejected = True
            return
            
        # Проверка длины отзыва
        min_len = settings.MODERATION_SETTINGS['MIN_LENGTH']
        max_len = settings.MODERATION_SETTINGS['MAX_LENGTH']
        if len(self.text) < min_len or len(self.text) > max_len:
            self.is_rejected = True
            return
            
        # Автоматическое одобрение для высоких оценок
        if self.rating >= settings.MODERATION_SETTINGS['MIN_RATING_FOR_AUTO_APPROVE']:
            self.is_approved = True
    def __str__(self):
        return f"Отзыв от {self.user.username} на {self.product.name}"
    
    def get_absolute_url(self):
        return reverse('shopapp:product_detail', kwargs={'id': self.product.pk})
    
    @staticmethod
    def get_average_rating(product_id):
        from django.db.models import Avg
        return Review.objects.filter(
            product_id=product_id, 
            is_approved=True,
            parent__isnull=True
        ).aggregate(Avg('rating'))['rating__avg'] or 0

class OrderStatusLog(models.Model):
    order = models.ForeignKey(Order, related_name='status_logs', on_delete=models.CASCADE)
    old_status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    new_status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ['-changed_at']

@receiver([post_save, post_delete], sender=Review)
def update_product_rating(sender, instance, **kwargs):
    """Обновляет средний рейтинг продукта при изменении отзывов"""
    product = instance.product
    average_rating = Review.get_average_rating(product.id)
    product.average_rating = average_rating
    product.save(update_fields=['average_rating'])