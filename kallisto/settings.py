"""
Django settings for kallisto project.
"""

import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DEBUG = 'true' == os.environ.get('DJANGO_DEBUG', 'true')
TEMPLATE_DEBUG = DEBUG

# Internationalization

LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Application definition

INSTALLED_APPS = (
    'apps.people',
    'apps.transcripts',
    'apps.homepage',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_cape',
    'exceptional_middleware',
)

MIDDLEWARE_CLASSES = (
#    'djangosecure.middleware.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.request",
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages"
)

ROOT_URLCONF = 'kallisto.urls'

WSGI_APPLICATION = 'kallisto.wsgi.application'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'kallisto.dev').split(';')

if DEBUG:
    SECRET_KEY = 't*cx2(5fbyuij4sf*-ct58=**isy=3rf0ue45yces1%9l%o5-q'
else:
    # Exception if this isn't set, ie can't accidentally run live with
    # the secret key in the source code.
    SECRET_KEY = os.environ['DJANGO_SECRET_KEY']


# This makes no sense under development, but is important when live.
if 'true' == os.environ.get('DJANGO_LIVE'):
    #SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    #CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True


# Email

ADMINS = (
    ('James Aylett', 'james@tartarus.org'),
)

MANAGERS = (
    ('James Aylett', 'james@tartarus.org'),
)

MANAGER_EMAILS = map(lambda x: u"%s <%s>" % (x[0], x[1]), MANAGERS)

if 'true' == os.environ.get('EMAILS_LIVE', 'false'): # pragma: no cover
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAILS_SMTP_HOST')
    EMAIL_HOST_USER = os.environ.get('EMAILS_SMTP_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAILS_SMTP_HOST_PASSWORD')
    EMAIL_PORT = os.environ.get('EMAILS_SMTP_PORT')
    EMAIL_USE_TLS = 'true' == os.environ.get('EMAILS_SMTP_USE_TLS', 'false')
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'Kallisto by Spacelog... <kallisto@spacelog.org>'
DEFAULT_TO_EMAIL = [ 'kallisto-errors@spacelog.org' ]
SERVER_EMAIL = 'kallisto-errors@spacelog.org'


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'kallisto',
        'USER': 'kallisto',
        'PASSWORD': 'kallisto',
     }
}
import dj_database_url
database = dj_database_url.config()
if database:
    DATABASES['default'] = database

# Templates

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

# Static files (CSS, JavaScript, Images) and media files

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
STATIC_ROOT = os.path.join(BASE_DIR, 'collected_static')
if 'test' not in sys.argv:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

MEDIA_ROOT = os.environ.get('MEDIA_ROOT')
if MEDIA_ROOT is None:
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

AUTH_USER_MODEL = 'people.User'
LOGIN_REDIRECT_URL = 'homepage'
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
