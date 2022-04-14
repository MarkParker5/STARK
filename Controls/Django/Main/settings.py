from pathlib import Path
import config


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config.django_secret_key

DEBUG = config.django_debug_enabled

ALLOWED_HOSTS = config.django_allowed_hosts

INSTALLED_APPS = [
    'django_extensions',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Controls.Django.api',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'Controls.Django.Main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [
            BASE_DIR / 'src',
        ],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Controls.Django.Main.wsgi.application'

# Internationalization

USE_I18N = False

USE_TZ = False

# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'database.sqlite3',
    }
}

AUTH_USER_MODEL = 'api.User'

# Static

STATIC_ROOT = BASE_DIR / 'static'
STATIC_URL = '/static/'

# Rest
