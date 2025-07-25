from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created']
    search_fields = ['name']
    list_filter = ['created']
    date_hierarchy = 'created'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'category_type', 'price', 'available', 'total_protein', 'created']
    list_filter = ['available', 'category', 'category_type', 'created']
    list_editable = ['price', 'available']
    search_fields = ['name', 'description']
    date_hierarchy = 'created'
    fieldsets = (
        (None, {
            'fields': (('category', 'category_type'), 'name', 'image')
        }),
        ('Детали', {
            'fields': ('description', ('price', 'protein_per_serving', 'servings'))
        }),
        ('Наличие', {
            'fields': ('available', 'is_featured')
        }),
    )