"""
Django settings for shop project.

Generated by 'django-admin startproject' using Django 5.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-2kn1pq3w3r&-!s4@5tio-yv$8(m!n4e^+)3kcp_k&7qsgv$hl7"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "shopapp.apps.ShopappConfig",  # Регистрация приложения
    "django.contrib.humanize",
    'rest_framework',
    'rest_framework.authtoken',
    
]


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    
]

ROOT_URLCONF = "shop.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                'cart.context_processors.cart',
            ],
        },
    },
]

WSGI_APPLICATION = "shop.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "sports",
        "USER": "postgres",
        "PASSWORD": "1",
        "HOST": "localhost",
        "PORT": "5432",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
CART_SESSION_ID = 'cart'


# settings.py
LOGIN_URL = 'shopapp:login'  # Полный путь с namespace
LOGIN_REDIRECT_URL = 'shopapp:product_list'  # Куда перенаправлять после входа
LOGOUT_REDIRECT_URL = 'shopapp:product_list'  # Куда перенаправлять после выхода
AUTH_USER_MODEL = 'shopapp.User'  # Указываем кастомную модель пользователя


REVIEW_SETTINGS = {
    'REQUIRE_PURCHASE': True,  # Требовать покупку товара для отзыва
    'AUTO_APPROVE_STAFF': True,  # Автоматически одобрять отзывы персонала
    'NOTIFY_ADMINS': True,  # Уведомлять админов о новых отзывах
    'ADMIN_EMAILS': ['shev.oleg200606@gmail.com'],  # Дополнительные email для уведомлений
}

# Добавьте в settings.py
MODERATION_SETTINGS = {
    'AUTO_MODERATION': True,  # Включить автоматическую модерацию
    'FORBIDDEN_WORDS': ['спам', 'реклама', 'мат', 'оскорбление'],  # Запрещенные слова
    'MIN_RATING_FOR_AUTO_APPROVE': 4,  # Минимальный рейтинг для автоматического одобрения
    'MIN_LENGTH': 10,  # Минимальная длина отзыва
    'MAX_LENGTH': 1000,  # Максимальная длина отзыва
}

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_SSL = False
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'shev.oleg200606@gmail.com'  # Ваш Gmail
EMAIL_HOST_PASSWORD = 'jkcr sxta xjsn pbwh'  # Пароль приложения
DEFAULT_FROM_EMAIL = 'client@gmail.com'

# URL админки для email-уведомлений
ADMIN_URL = 'http://http://127.0.0.1:8000/admin/'