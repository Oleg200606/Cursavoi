# Generated by Django 5.1.7 on 2025-05-02 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shopapp", "0003_alter_cart_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="order_number",
            field=models.CharField(blank=True, max_length=20, unique=True),
        ),
    ]
