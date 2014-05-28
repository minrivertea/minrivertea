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


DEBUG =                         False
GA_IS_ON =                      True
TEMPLATE_DEBUG =                DEBUG
THUMBNAIL_DEBUG =               False
GA_IS_ON =                      True
ADMINS =                        (('Chris West', 'chris@minrivertea.com'),)
MANAGERS =                      ADMINS
NOTIFICATIONS_GROUP =           (
                                    ('Chris West', 'chris@minrivertea.com'), 
                                    ('Raphael Henkes', 'raphael@minrivertea.com'),
                                )
TIME_ZONE =                     'Europe/London'
SITE_ID =                       1
SITE_NAME =                     'minrivertea.com'
SITE_URL =                      'http://www.minrivertea.com'
ANALYTICS_ID =                  'UA-9041614-4'
MAILCHIMP_LIST_ID =             'cde5cb0d9e'
GERMAN_URL =                    'www.minrivertea.de'
GERMAN_ANALYTICS_ID =           'UA-9041614-9'
GERMAN_MAILCHIMP_LIST_ID =      '9fd8b080b7'
ITALIAN_URL =                   'www.minrivertea.it'
ITALIAN_ANALYTICS_ID =          ''
ITALIAN_MAILCHIMP_LIST_ID =     '07a453a7b5'
SECRET_KEY =                    ''

# SSL IMPORTANT STUFF
SESSION_COOKIE_SECURE =         False 
CSRF_COOKIE_SECURE =            False 
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SECURE_PROXY_SSL_HEADER =       ('HTTP_X_FORWARDED_PROTOCOL', 'https') 


# STATIC / MEDIA FILES
# ----------------------------------------------------------
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')
MEDIA_URL = 'https://www.minrivertea.com/media/'

STATIC_URL = 'https://www.minrivertea.com/static/'
STATICFILES_DIRS = (
    os.path.join(PROJECT_PATH, 'static'),
)


TEMPLATE_LOADERS = (
#    'ab.loaders.load_template_source',
#    'django.template.loaders.filesystem.load_template_source',
    'django_mobile.loader.Loader',
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
    'django_mobile.context_processors.flavour',
)


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware', 
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
#    'ab.middleware.ABMiddleware',
    'django_mobile.middleware.MobileDetectionMiddleware',
    'django_mobile.middleware.SetFlavourMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'affiliate.AffiliateTrackerMiddleware',
    'sites.DomainTrackerMiddleware'
)

AUTHENTICATION_BACKENDS = (
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
    'django.contrib.staticfiles',
    'shop',
    'blog',
    'emailer',
    'sorl.thumbnail',
    'paypal.standard.ipn',
    'registration',
#    'ab',
    'django_mobile',
    'south',
    'my_admin',
    'captcha',
    'rosetta',
    'modeltranslation_wrapper',
    'modeltranslation',
    'logistics',
    'emailer',
    'ckeditor',
    'premailer',
)



APPEND_SLASH = True

# MAIL SETTINGS
# -----------------------------------------------
EMAIL_HOST = ''
EMAIL_HOST_USER = ''
EMAIL_PORT = ''
SERVER_EMAIL = 'chris@minrivertea.com'
SITE_EMAIL = 'Chris from MinRiverTea.com <mail@minrivertea.com>'
SEND_BROKEN_LINK_EMAILS = False
EMAIL_BASE_HTML_TEMPLATE = 'emailer/email_base.html'
EMAIL_BACKEND = 'emailer.backend.DKIMBackend'
DKIM_SELECTOR = 'selector'
DKIM_DOMAIN = 'minrivertea.com'




#THUMBNAIL SIZES
# -----------------------------------------------
THUMB_LARGE = "500x331"
THUMB_HOME_LARGE = "375x240"
THUMB_MEDIUM = "240x160"
THUMB_SMALL = "50x50"


# REGIONAL TEMPLATES
# -----------------------------------------------
BASE_TEMPLATE = 'base.html'
BASE_TEMPLATE_CHINA = 'base_china.html'
BASE_TEMPLATE_ADMIN = 'base_admin.html'



# DJANGO-CAPTCHA
# -----------------------------------------------
CAPTCHA_FONT_SIZE = 35
CAPTCHA_LETTER_ROTATION = None


# DISCOUNTS
# -----------------------------------------------
TEABOX_LOW_DISCOUNT = 0.1 # expressed as a percentage, eg. 0.1 is 10% off
TEABOX_HIGH_DISCOUNT = 0.15 # expressed as a percentage, eg. 0.1 is 10% off
TEABOX_DEFAULT_MONTHS = 6

# DJANGO SOUTH
# -----------------------------------------------
SOUTH_TESTS_MIGRATE = False


# CKEDITOR SETTINGS
# -----------------------------------------------
CKEDITOR_UPLOAD_PATH = os.path.join(MEDIA_ROOT, 'ckuploads')
CKEDITOR_UPLOAD_PREFIX = "/media/ckuploads/"
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': [
            [      'Undo', 'Redo',
              '-', 'Bold', 'Italic', 'Underline', 'BulletedList', 'NumberedList', 'Image',
              '-', 'Link', 'Unlink', 'Anchor',
              '-', 'Format',
              '-', 'PasteFromWord',
              '-', 'Maximize', 'Source', 
            ],
        ],
        'width': 840,
        'height': 300,
        'toolbarCanCollapse': False,
    }
}

# LANGUAGE SETTINGS
# ------------------------------------------
USE_I18N = True
gettext = lambda s: s
LANGUAGES = (
    ('en', gettext('English')),
    ('de', gettext('German')),
    ('it', gettext('Italian')),
)

MODEL_LANGUAGES = (
    ('en', gettext('English')),
    ('de', gettext('German')),
    ('it', gettext('Italian')),
)

LOCALE_PATHS = (
    os.path.join(PROJECT_PATH, "locale"),
)

LANGUAGE_CODE = 'en'
LANGUAGE_COOKIE_NAME = 'django_language'

MODELTRANSLATION_TRANSLATION_REGISTRY = "translation"
MODELTRANSLATION_DEFAULT_LANGUAGE = 'en'



# AFFILIATE SETTINGS
# ---------------------------------------------------
AFFILIATE_URL_VARIABLE = 'sales_adforce'
AFFILIATE_SESSION_KEY = 'affiliate'


# MOBILE SETTINGS
# ---------------------------------------------------

FLAVOURS = ('full', 'mobile')
DEFAULT_MOBILE_FLAVOUR = 'mobile'



# PAYPAL INFORMATION
# ---------------------------------------------------
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
