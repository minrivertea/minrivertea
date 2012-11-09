# Django settings for minriver project.

import os
PROJECT_PATH = os.path.normpath(os.path.dirname(__file__))

DEBUG = False
TEMPLATE_DEBUG = DEBUG
THUMBNAIL_DEBUG = False
GA_IS_ON = True



ADMINS = (
    ('Chris West', 'chris@minrivertea.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = ''           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = ''             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.




TIME_ZONE = 'Europe/London'
SITE_ID = 1
SITE_URL = "http://www.minrivertea.com"




# STATIC / MEDIA FILES
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'static')
MEDIA_URL = ''
ADMIN_MEDIA_PREFIX = '/admin/media/'


# Make this unique, and don't share it with anybody.
SECRET_KEY = ''


TEMPLATE_LOADERS = (
    'django_mobile.loader.Loader',
    'ab.loaders.load_template_source',
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.media',
    'django.core.context_processors.debug',
    'django.core.context_processors.request',
    'minriver.shop.context_processors.get_shopper',
    'minriver.shop.context_processors.common',
    'django_mobile.context_processors.flavour',
)


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware', 
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'ab.middleware.ABMiddleware',
#    'django_mobile.middleware.MobileDetectionMiddleware',
#    'django_mobile.middleware.SetFlavourMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
#    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

AUTHENTICATION_BACKENDS = (
    "emailauth.EmailBackend",
    "django.contrib.auth.backends.ModelBackend",
)


ROOT_URLCONF = 'minriver.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, "templates/"), 
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.sitemaps',
    'django.contrib.comments',
    'django.contrib.redirects',
    'shop',
    'blog',
    'sorl.thumbnail',
    'paypal.standard.ipn',
    'django_static',
    'registration',
#    'ab',
#    'django_mobile',
    'south',
    'my_admin',
    'my_comments',
    'captcha',
    'rosetta',
    'modeltranslation',
    'modeltranslation_wrapper',
    'logistics',
    'emailer',
#    'debug_toolbar',
)

# Random app information for different things
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# django-static info
DJANGO_STATIC = True
DJANGO_STATIC_SAVE_PREFIX = '/tmp/cache-forever'
DJANGO_STATIC_NAME_PREFIX = '/cache-forever'
DJANGO_STATIC_MEDIA_URL = 'http://static.minrivertea.com'

# mail settings
EMAIL_HOST = ''
EMAIL_HOST_USER = ''
EMAIL_PORT = ''
SERVER_EMAIL = 'chris@minrivertea.com'
SITE_EMAIL = 'Chris from MinRiverTea.com <mail@minrivertea.com>'
SEND_BROKEN_LINK_EMAILS = False

#THUMBNAIL SIZES
THUMB_LARGE = "500x331"
THUMB_MEDIUM = "240x160"
THUMB_SMALL = "50x50"


# REGIONAL TEMPLATES
BASE_TEMPLATE = 'base.html'
BASE_TEMPLATE_CHINA = 'base_china.html'
BASE_TEMPLATE_ADMIN = 'base_admin.html'

# DJANGO-CAPTCHA
COMMENTS_APP = 'my_comments'
CAPTCHA_FONT_SIZE = 35
CAPTCHA_LETTER_ROTATION = None

EMAIL_TEMPLATES = (

)

# LANGUAGE SETTINGS
LANGUAGE_CODE = 'en'
USE_I18N = True
gettext = lambda s: s
LANGUAGE_CODE = 'en'
LANGUAGES = (
    ('en', gettext('English')),
    ('de', gettext('German')),
)
LOCALE_PATHS = (
    os.path.join(PROJECT_PATH, "locale"),
)
LANGUAGE_COOKIE_NAME = 'django_language'
MODELTRANSLATION_TRANSLATION_REGISTRY = "translation"


# paypal info
PAYPAL_IDENTITY_TOKEN = ''
PAYPAL_RECEIVER_EMAIL = ''
PAYPAL_RETURN_URL = ''
PAYPAL_NOTIFY_URL = ''
PAYPAL_BUSINESS_NAME = ''
PAYPAL_SUBMIT_URL = 'https://www.paypal.com/cgi-bin/webscr'


LOG_FILENAME = ""

try:
    from local_settings import *
except ImportError:
    pass

import logging 
                    
logging.basicConfig(filename=LOG_FILENAME,
                   level=logging.DEBUG,
                   datefmt="%Y-%m-%d %H:%M:%S",
                   format="%(asctime)s %(levelname)s %(name)s %(message)s",
                  )
