from django.db import models
from shopapp.models import Product

class Cart(models.Model):
    cart_id = models.CharField(max_length=50, blank=True)
    date_added = models.DateField(auto_now_add=True)
    
    class Meta:
        db_table = 'Cart'
        ordering = ['date_added']
    
    def __str__(self):
        return self.cart_id

class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'CartItem'
    
    def sub_total(self):
        return self.product.price * self.quantity
    
    def __str__(self):
        return self.product.name