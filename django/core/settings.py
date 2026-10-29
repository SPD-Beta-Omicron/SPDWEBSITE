"""
Django settings for the SPD website.

Secrets live in a .env file in STORAGE_DIR (see WebsiteRedeploy/.env.example).
Setting reference: https://docs.djangoproject.com/en/6.1/ref/settings/
"""

import os
from pathlib import Path

from dotenv import load_dotenv


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

# The django/ folder that holds manage.py
BASE_DIR = Path(__file__).resolve().parent.parent

# Always store outside the git repo. Holds .env, db.sqlite3, media/ and staticfiles/
# Note that this only works if the docker container is run with the STORAGE_DIR environment variable is set in the run command, the dockerfil, the compose file, or the process environment.
# This cannot be loaded from .env because .env is stored in STORAGE_DIR, so we need to get STORAGE_DIR from the environment first.
# # In the dockerfile, this will default to STORAGE_DIR=/data
# If STORAGE_DIR is not set, it defaults to the parent of the parent of BASE_DIR (one above the root of the git repo).
STORAGE_DIR = Path(os.environ.get('STORAGE_DIR', BASE_DIR.parent.parent))


# ---------------------------------------------------------------------------
# Secrets and environment (from .env)
# ---------------------------------------------------------------------------

load_dotenv(STORAGE_DIR / '.env')

def require_env(name):
    value = os.environ.get(name)
    if not value:
        raise ValueError(f"No {name} found! Make sure the .env file exists in {STORAGE_DIR}")
    return value

SECRET_KEY = require_env('SECRET_KEY')

# Path of the admin site, used in urls.py
ADMIN_URL = require_env('ADMIN_URL')

# 'production' on the server, anything else (e.g. 'local') for development
ENVIRONMENT = require_env('ENVIRONMENT')

DEBUG = ENVIRONMENT != 'production'

# Comma-separated domains this site answers to, e.g. 'localhost,127.0.0.1'
ALLOWED_HOSTS = [host.strip() for host in require_env('ALLOWED_HOSTS').split(',') if host.strip()]


# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'adminsortable2',

    # SPD apps
    'authenticate',
    'polls',
    'misc',
    'philanthropy',
    'newmember',
    'sobersheet',
    'home',
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

ROOT_URLCONF = 'core.urls'
WSGI_APPLICATION = 'core.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
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


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': STORAGE_DIR / 'db.sqlite3',
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ---------------------------------------------------------------------------
# Login and passwords
# ---------------------------------------------------------------------------

LOGIN_URL = '/auth/login'
LOGIN_REDIRECT_URL = ''

AUTH_PASSWORD_VALIDATORS = [
    # Rejects passwords too similar to the username or email
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    # Rejects passwords on a list of common passwords
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    # Rejects passwords that are entirely numbers
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ---------------------------------------------------------------------------
# Language and time
# ---------------------------------------------------------------------------

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Chicago'
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------------
# Static files (CSS, JS, images) and media (user uploads)
# ---------------------------------------------------------------------------

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = STORAGE_DIR / 'staticfiles'     # filled by `manage.py collectstatic`, served by nginx

MEDIA_URL = '/media/'
MEDIA_ROOT = STORAGE_DIR / 'media'            # served by nginx in production


# ---------------------------------------------------------------------------
# Production-only security
# ---------------------------------------------------------------------------

if ENVIRONMENT == 'production':
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
    # nginx terminates HTTPS and tells Django the original request was secure
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # HSTS forces browsers to use HTTPS for this many seconds (3 days).
    # If the SSL certificate ever breaks, these must be turned off.
    SECURE_HSTS_SECONDS = 259200
    SECURE_HSTS_PRELOAD = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
