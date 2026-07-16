"""
Django settings for the Ecommerence project.

This file configures the entire application: installed apps, middleware,
authentication (JWT via Simple JWT), REST framework, CORS, media handling,
and email/notification backends. Sensible defaults are provided so the
project runs out of the box; override them with environment variables
or a .env file for production.
"""

from pathlib import Path

import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


def env(key, default=None):
    """Read an environment variable or return a default value."""
    return os.environ.get(key, default)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/stable/howto/deployment/checklist/

SECRET_KEY = env(
    'SECRET_KEY',
    'django-insecure-cjba6n4$1bgnn&zug9q7*v488ighs3uq9z#)sy7q$uo)rmonm-',
)

DEBUG = env('DEBUG', 'True').lower() in ('1', 'true', 'yes', 'on')

ALLOWED_HOSTS = env('ALLOWED_HOSTS', '*').split(',')


# Application definition

INSTALLED_APPS = [
    # Django default apps.
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps.
    'rest_framework',
    'django_filters',
    'corsheaders',
    'drf_spectacular',

    # Local apps.
    'core',
    'accounts',
    'categories',
    'products',
    'cart',
    'orders',
    'payments',
    'reviews',
    'wishlist',
    'coupons',
    'notifications',
    'dashboard',
    'api',
]


MIDDLEWARE = [
    # Django default middleware.
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Cross-origin support for a decoupled frontend.
    'corsheaders.middleware.CorsMiddleware',

    # Custom request logging / context middleware.
    'core.middleware.RequestMetaMiddleware',
]


ROOT_URLCONF = 'eCommerce.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'Templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Global template context (cart count, categories, etc.).
                'core.context_processors.global_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'eCommerce.wsgi.application'


# Database
# https://docs.djangoproject.com/en/stable/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/stable/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/stable/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/stable/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files (uploaded product images, avatars, ...).
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Default primary key field type.
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Tell Django to use the custom User model defined in accounts.
AUTH_USER_MODEL = 'accounts.User'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

AUTHENTICATION_BACKENDS = [
    'accounts.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Email configuration.
# In development emails are printed to the console instead of being sent.
EMAIL_BACKEND = env(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend',
)
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', 'noreply@ecommerence.com')
EMAIL_HOST = env('EMAIL_HOST', 'smtp.example.com')
EMAIL_PORT = int(env('EMAIL_PORT', '587'))
EMAIL_HOST_USER = env('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = env('EMAIL_USE_TLS', 'True').lower() in ('1', 'true', 'yes', 'on')


# CORS settings for local development.
CORS_ALLOW_ALL_ORIGINS = env('CORS_ALLOW_ALL_ORIGINS', 'True').lower() in (
    '1', 'true', 'yes', 'on'
)
CORS_ALLOW_CREDENTIALS = True


# REST framework configuration.
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'api.pagination.StandardPagination',
    'PAGE_SIZE': 12,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'api.exceptions.standard_exception_handler',
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}


# Simple JWT configuration.
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_SETTINGS': 'eCommerce.settings',
}


# drf-spectacular (OpenAPI / Swagger) configuration.
SPECTACULAR_SETTINGS = {
    'TITLE': 'Ecommerence API',
    'DESCRIPTION': 'Complete e-commerce REST API.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDES': [],
    'SCHEMA_PATH_PREFIX': '/api',
}


# Payment provider credentials (leave blank to disable live mode).
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY', '')
STRIPE_PUBLISHABLE_KEY = env('STRIPE_PUBLISHABLE_KEY', '')
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET', '')

PAYPAL_CLIENT_ID = env('PAYPAL_CLIENT_ID', '')
PAYPAL_CLIENT_SECRET = env('PAYPAL_CLIENT_SECRET', '')
PAYPAL_MODE = env('PAYPAL_MODE', 'sandbox')  # 'sandbox' or 'live'


# Storefront behaviour toggles.
LOW_STOCK_THRESHOLD = int(env('LOW_STOCK_THRESHOLD', '5'))
DEFAULT_TAX_RATE = float(env('DEFAULT_TAX_RATE', '0.0'))
DEFAULT_SHIPPING_FLAT_RATE = float(env('DEFAULT_SHIPPING_FLAT_RATE', '0.0'))
FREE_SHIPPING_THRESHOLD = float(env('FREE_SHIPPING_THRESHOLD', '0.0'))
