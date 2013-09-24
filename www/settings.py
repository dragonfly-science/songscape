# Django settings for www project.
import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Christopher Knox', 'chris@dragonfly.co.nz'),
)

# This directory
PROJECT_DIR = os.path.dirname(__file__)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'songscape',
        'USER': 'songscape',
        'PASSWORD': '***',
        'HOST': 'localhost',
        'PORT': '',
    }
}

#TIME_ZONE = 'Pacific/Auckland'
LANGUAGE_CODE = 'en-nz'
USE_I18N = True
USE_L10N = True

SITE_ID = 1

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(PROJECT_DIR, '../static/')

STATICFILES_DIRS = (
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_DIR, 'static'),
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_DIR, "templates"),
)

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

ADMIN_MEDIA_PREFIX = '/static/admin/'

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
   'django.contrib.auth.context_processors.auth',
   'django_browserid.context_processors.browserid',
   'django.core.context_processors.request',
   'django.core.context_processors.media',
   'django.core.context_processors.debug',
   'django.contrib.messages.context_processors.messages',
   'django.core.context_processors.request',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
#    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

ROOT_URLCONF = 'www.urls'

LOGIN_REDIRECT_URL = '/'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django_browserid',  # Load after auth
    'django.contrib.contenttypes',
    'django.contrib.sessions',
     'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',

    'www.recordings',
    'south',
    'django_nose',
    #'debug_toolbar',
)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [ '--with-xunit', '--with-doctest', ]

INTERNAL_IPS = ('127.0.0.1',)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
    'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
            'filters': ['require_debug_false'],
        },
        'django_browserid': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}

RECORDINGS_PATH = '' # Path of the raw recordings

# organisation repositories. A dictionary with keys
# being the organisation codes, and values
# being the URLs of the servers that hold the
# raw recordings
#REPOSITORIES = {'RFPT': 'http://rfpt.songscape.org'}
REPOSITORIES = {'RFPT': 'http://192.168.0.123:8888'}

# Set your site url for security
SITE_URL = 'http://localhost:8000'

DEBUG_TOOLBAR_CONFIG = {'INTERCEPT_REDIRECT': False}

# Add the django_browserid authentication backend.
AUTHENTICATION_BACKENDS = (
   'django.contrib.auth.backends.ModelBackend', # required for admin
   'django_browserid.auth.BrowserIDBackend',
)

#SESSION_COOKIE_SECURE = False

# Path to redirect to on successful login.
LOGIN_REDIRECT_URL = '/'

# Path to redirect to on unsuccessful login attempt.
LOGIN_REDIRECT_URL_FAILURE = '/'

# Path to redirect to on logout.
LOGOUT_REDIRECT_URL = '/'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake'
    }
}

try:
    from local_settings import *
except ImportError:
    print "Error loading local settings"
    pass

# MEDIA_ROOT can be overridden in local_settings
SONOGRAM_DIR = 'sonograms/'
SNIPPET_DIR = 'snippets/'


import sys
#if manage.py test was called, use test settings
if 'test' in sys.argv or 'migrationcheck' in sys.argv:
    try:
        from .test_settings import *
    except ImportError:
        print "Can't find test_settings.py"

