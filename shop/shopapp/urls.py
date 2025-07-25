from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    ProductViewSet, CategoryViewSet,
    CartViewSet, OrderViewSet
)
from . import views
from django.contrib.auth import views as auth_views

app_name = 'shopapp'

# API Router
router = DefaultRouter()
router.register(r'api/products', ProductViewSet, basename='product')
router.register(r'api/categories', CategoryViewSet, basename='category')
router.register(r'api/carts', CartViewSet, basename='cart')
router.register(r'api/orders', OrderViewSet, basename='order')

urlpatterns = [
    # API Endpoints
    path('api/', include(router.urls)),
    
    # API Documentation
    path('api-docs/', views.APIDocsView.as_view(), name='api_docs'),
    
    # Main App URLs
    path('', views.product_list, name='product_list'),
    path('catalog/', views.catalog, name='catalog'),
    path('catalog/<int:category_id>/', views.catalog, name='catalog_by_category'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    
    # Admin URLs
    path('product/add/', views.product_create, name='product_create'),
    path('product/<int:id>/edit/', views.product_edit, name='product_edit'),
    path('product/<int:id>/delete/', views.product_delete, name='product_delete'),
    
    path('category/add/', views.category_create, name='category_create'),
    path('category/<int:id>/edit/', views.category_edit, name='category_edit'),
    path('category/<int:id>/delete/', views.category_delete, name='category_delete'),

    # User URLs
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    
    # Cart URLs
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),

    # Order URLs
    path('checkout/', views.checkout, name='checkout'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/', views.order_history, name='order_history'),

    # Auth URLs
    path('accounts/login/', auth_views.LoginView.as_view(template_name='shopapp/auth/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='shopapp:product_list'), name='logout'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(
        template_name='shopapp/auth/password_reset.html',
        email_template_name='shopapp/auth/password_reset_email.html',
        subject_template_name='shopapp/auth/password_reset_subject.txt'
    ), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='shopapp/auth/password_reset_done.html'
    ), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='shopapp/auth/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='shopapp/auth/password_reset_complete.html'
    ), name='password_reset_complete'),

    # Reviews URLs
    path('product/<int:product_id>/review/', views.add_review, name='add_review'),
    path('review/<int:review_id>/reply/', views.add_review_reply, name='add_review_reply'),
    path('reviews/moderation/', views.review_moderation, name='review_moderation'),
    path('reviews/<int:review_id>/approve/', views.approve_review, name='approve_review'),
    path('reviews/<int:review_id>/reject/', views.reject_review, name='reject_review'),

    # Other URLs
    path('promotions/', views.promotions, name='promotions'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('about/', views.about, name='about'),
]