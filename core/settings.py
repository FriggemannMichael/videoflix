"""Django settings for the core project."""

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv(
    'SECRET_KEY',
    default='django-insecure-@#x5h3zj!g+8g1v@2^b6^9$8&f1r7g$@t3v!p4#=g0r5qzj4m3',
)

DEBUG = os.environ.get('DEBUG', default='True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', default='localhost').split(',')
CSRF_TRUSTED_ORIGINS = os.environ.get(
    'CSRF_TRUSTED_ORIGINS', default='http://localhost:4200'
).split(',')

FRONTEND_URL = os.environ.get('FRONTEND_URL', default='http://localhost:5500')

# The frontend may be opened on either host name, so both are allowed by
# default and the configured FRONTEND_URL is always included.
CORS_ALLOWED_ORIGINS = list(
    dict.fromkeys(
        os.environ.get(
            'CORS_ALLOWED_ORIGINS',
            default='http://localhost:5500,http://127.0.0.1:5500',
        ).split(',')
        + [FRONTEND_URL]
    )
)
CORS_ALLOW_CREDENTIALS = True

# The provided frontend hardcodes the API host as 127.0.0.1:8000 while being
# served from localhost:5500, so the auth cookies must survive a cross-site
# request. 'None' requires 'Secure', which browsers also accept over plain HTTP
# on trustworthy origins (localhost / 127.0.0.1).
AUTH_COOKIE_SAMESITE = os.environ.get('AUTH_COOKIE_SAMESITE', default='None')
AUTH_COOKIE_SECURE = os.environ.get('AUTH_COOKIE_SECURE', default='True') == 'True'

PASSWORD_RESET_TIMEOUT = 60 * 60 * 24  # 24 hours

EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend'
)
EMAIL_HOST = os.environ.get('EMAIL_HOST', default='localhost')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', default=587))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', default='True') == 'True'
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', default='False') == 'True'
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', default='webmaster@localhost')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_rq',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'accounts',
    'videos',
]

AUTH_USER_MODEL = 'accounts.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'accounts.authentication.CookieJWTAuthentication',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(
        minutes=int(os.environ.get('ACCESS_TOKEN_LIFETIME_MINUTES', default=60))
    ),
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'core.middleware.TrustedOriginMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', default='videoflix_db'),
        'USER': os.environ.get('DB_USER', default='videoflix_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', default='supersecretpassword'),
        'HOST': os.environ.get('DB_HOST', default='db'),
        'PORT': os.environ.get('DB_PORT', default=5432),
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_LOCATION', default='redis://redis:6379/1'),
        'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
        'KEY_PREFIX': 'videoflix',
    }
}

RQ_QUEUES = {
    'default': {
        'HOST': os.environ.get('REDIS_HOST', default='redis'),
        'PORT': os.environ.get('REDIS_PORT', default=6379),
        'DB': os.environ.get('REDIS_DB', default=0),
        'DEFAULT_TIMEOUT': 900,
        'REDIS_CLIENT_KWARGS': {},
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': (
            'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'
        ),
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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

FFMPEG_PATH = os.environ.get('FFMPEG_PATH', default='ffmpeg')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
