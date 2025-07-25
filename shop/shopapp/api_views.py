from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db import transaction
from .models import Product, Category, Cart, CartItem, Order, OrderItem
from .serializers import (
    ProductSerializer, CategorySerializer,
    CartSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer
)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'toggle_available']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['post'])
    def toggle_available(self, request, pk=None):
        product = self.get_object()
        product.available = not product.available
        product.save()
        return Response({
            'status': 'success',
            'message': f'Product availability set to {product.available}',
            'available': product.available
        })


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]




class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Cart.objects.none()

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user).prefetch_related('items')

    @action(detail=False, methods=['get'])
    def my_cart(self, request):
        cart = self.get_queryset().first()
        if not cart:
            cart = Cart.objects.create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        serializer = CartItemSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        cart = self.get_queryset().first() or Cart.objects.create(user=request.user)
        product = serializer.validated_data['product']
        quantity = serializer.validated_data.get('quantity', 1)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return Response(
            CartItemSerializer(cart_item).data,
            status=status.HTTP_201_CREATED
        )


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Order.objects.none()

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')

    @transaction.atomic
    def perform_create(self, serializer):
        cart = Cart.objects.filter(user=self.request.user).first()
        if not cart or not cart.items.exists():
            raise ValidationError("Your cart is empty")

        order = serializer.save(user=self.request.user)
        
        for item in cart.items.all():
            if not item.product.available:
                raise ValidationError(
                    f"Product {item.product.name} is not available"
                )
            
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,
                quantity=item.quantity
            )
        
        cart.items.all().delete()
        return order