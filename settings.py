# Django settings for minriver project.

import os
PROJECT_PATH = os.path.normpath(os.path.dirname(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}


DEBUG = False
TEMPLATE_DEBUG = DEBUG
THUMBNAIL_DEBUG = False
GA_IS_ON = True
ADMINS = (('Chris West', 'chris@minrivertea.com'),)
MANAGERS = ADMINS
TIME_ZONE = 'Europe/London'
SITE_ID = 1
SITE_URL = "http://www.minrivertea.com"
SECRET_KEY = ''



# STATIC / MEDIA FILES
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'static') # the place where user-uploaded files should sit in the filesystem
MEDIA_URL = '/' # the public URL for user uploaded files
STATIC_URL = '/static/' # the public URL for static files




TEMPLATE_LOADERS = (
#    'ab.loaders.load_template_source',
#    'django_mobile.loader.Loader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.media',
    'django.core.context_processors.debug',
    'django.core.context_processors.request',
    'shop.context_processors.get_shopper',
    'shop.context_processors.common',
#    'django_mobile.context_processors.flavour',
)


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware', 
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
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


ROOT_URLCONF = 'urls'

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
    'modeltranslation_wrapper',
    'modeltranslation',
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
THUMB_HOME_LARGE = "375x240"
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

SOUTH_TESTS_MIGRATE = False

EMAIL_TEMPLATES = (

)

# LANGUAGE SETTINGS
# ------------------------------------------
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
MODELTRANSLATION_DEFAULT_LANGUAGE = 'en'


REPEAT_FREQUENCIES = (
    ('12', gettext('12 Months')),
    ('6', gettext('6 Months')),
    ('3', gettext('3 Months')),
)

MONTHLY_ORDER_AMOUNTS = (
    ('1', gettext('100g')),
    ('2', gettext('200g')),
    ('3', gettext('300g')),
    ('5', gettext('500g')),
    ('10', gettext('1kg')),
)

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
