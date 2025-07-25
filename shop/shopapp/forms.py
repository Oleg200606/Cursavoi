from django import forms
from .models import Product, Category, User, Order, Review
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

class ProductForm(forms.ModelForm):
    servings = forms.IntegerField(
        label='Количество порций',
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Product
        fields = ['category', 'category_type', 'name', 'image', 
                 'description', 'price', 'available', 'is_featured', 
                  'protein_per_serving', 'servings']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'phone_number']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_address', 'phone', 'full_name', 'notes']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Оставьте ваш отзыв здесь...',
                'class': 'form-control'
            }),
            'rating': forms.RadioSelect(
                choices=[(i, i) for i in range(1, 6)],
                attrs={'class': 'rating-radio'}
            ),
        }
        labels = {
            'text': 'Ваш отзыв',
            'rating': 'Оценка'
        }
    
    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating not in range(1, 6):
            raise ValidationError("Оценка должна быть от 1 до 5")
        return rating