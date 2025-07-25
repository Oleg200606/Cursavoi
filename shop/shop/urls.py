from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from shopapp import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shopapp.urls')),
    path('cart/', include('cart.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


