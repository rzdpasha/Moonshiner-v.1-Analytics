import environ
import os
import sys
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, 'django-insecure-build'),
    DATABASE_URL=(str, 'postgres://moonshiner:homebrew@localhost:5432/m1'),
    # REDIS_URL=(str, 'redis://127.0.0.1:6379/0'),
    ALLOWED_HOSTS=(list, ['127.0.0.1', 'localhost']),
    EMAIL_BACKEND=(str, 'django.core.mail.backends.console.EmailBackend'),
    EMAIL_HOST=(str, 'smtp.mail.ru'),
    EMAIL_PORT=(int, 465),
    EMAIL_HOST_USER=(str, 'info@rzdpasha.ru'),
    EMAIL_HOST_PASSWORD=(str, 'dummy-password'),
    EMAIL_USE_SSL=(bool, True),
    EMAIL_USE_TLS=(bool, False),
    CSRF_TRUSTED_ORIGINS=(str, "http://10.8.0.4"),
    CORS_ALLOWED_ORIGINS=(str, "http://10.8.0.4"),
    # CELERY_BROKER_URL = (str, 'redis://127.0.0.1:6379/1'),
    # CELERY_RESULT_BACKEND = (str, 'redis://127.0.0.1:6379/1')

)

if os.path.exists("/etc/moonshiner.env"):
    ENV_FILE = "/etc/moonshiner.env"
else:
    ENV_FILE = BASE_DIR / ".env"


if os.path.exists(ENV_FILE):
    environ.Env.read_env(str(ENV_FILE))

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# 4. Секция базы данных (универсальная)
DATABASES = {
    'default': env.db(),
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # 'django_extensions',
    "homebrew.apps.HomebrewConfig",
    "reports.apps.ReportsConfig",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'M1.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

WSGI_APPLICATION = 'M1.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'moonshiner',
#         'USER': 'moonshiner',
#         'PASSWORD': 'homebrew',
#         'HOST': '127.0.0.1',
#         'PORT': '5432',
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = "ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/


LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = 'login'