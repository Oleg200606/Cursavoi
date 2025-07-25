from django.apps import AppConfig


class ShopappConfig(AppConfig):  # Или ShopappConfig, если у вас так
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shopapp'  # или 'shopapp'

    def ready(self):
        import shopapp.signals 

