import sys
sys.path.append('../') # backend/

import os
from pathlib import Path
from config import project_settings


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = project_settings.DJANGO_SECRET_KEY

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    # Internal apps
    'apps.auth.apps.AuthConfig',

    # Django apps
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    # Django middleware
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Internal middleware
    'beton.middleware.ExceptionMiddleware',
    'beton.middleware.RateLimitMiddleware',
]

ROOT_URLCONF = 'beton.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'templates/errors'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'beton.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'options': '-c search_path=public'
        },
        'HOST': project_settings.DB_HOST,
        'PORT' : project_settings.DB_PORT,
        'NAME': project_settings.DB_NAME,
        'USER': project_settings.DB_USER,
        'PASSWORD': project_settings.DB_PASSWORD,
        'ATOMIC_REQUESTS': True,
    },
}

# Internationalization
LANGUAGE_CODE = 'ru-RU'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATICFILES_DIRS = []
if DEBUG is False:
    STATIC_ROOT = 'static'
else:
    STATICFILES_DIRS.append(os.path.join(BASE_DIR, 'static'))

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
