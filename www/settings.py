# Django settings for www project.
import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Joel Pitt', 'joel@dragonfly.co.nz'),
)

# What is GIT_HOME? Can we create it from the settings file path?
#from local_settings import GIT_HOME, RECORDINGS_PATH
GIT_HOME = os.path.dirname(__file__)
#RECORDINGS_PATH = os.path.dirname(__file__)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', 
        'NAME': 'songscape',
        'USER': 'dba',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '',
    }
}

TIME_ZONE = 'Pacific/Auckland'
LANGUAGE_CODE = 'en-nz'
USE_I18N = True
USE_L10N = True

SITE_ID = 1

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(GIT_HOME, 'media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

STATICFILES_DIRS = (
    # Don't forget to use absolute paths, not relative paths.
    # ... I don't think we want to collect/copy all the recordings data when
    # we run collectstatic
    #RECORDINGS_PATH,
    os.path.join(GIT_HOME, 'static/'),
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(GIT_HOME, "www/templates"),
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

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'www.urls'

LOGIN_REDIRECT_URL = '/'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    # 'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'django.contrib.admin',
    'django.contrib.admindocs',

    'recordings',
    'south',
)

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
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
            'filters': ['require_debug_false'],
        },
    }
}

# Is RECORDINGS_PATH the root for the other 3?
RECORDINGS_PATH = ''
SONOGRAM_DIR = 'sonograms/'
MP3_DIR = 'mp3/' # this was joined with RECORDINGS_PATH
DATA_DIR = 'data/' # this was joined with RECORDINGS_PATH

try:
    from local_settings import *
except ImportError:
    pass


