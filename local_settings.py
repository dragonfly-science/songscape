# Be careful with this file, as it is used as a template for the debian
# package setup. Feel free to copy it to local_settings.py and change/fill in
# as you like though.

DATABASES = {
    'default': {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": 'songscape_dev',
        "USER": 'birdsong',
        "PORT": '5000',
        "HOST": 'localhost',
        "PASSWORD": 'golgeinEnImvaur',
    }
}
# Change this to True if you are doing local development
DEBUG = True

SITE_URL = ''
MEDIA_ROOT = '/home/jasonhideki/songscape/www/media'

EMAIL_HOST = ''
SERVER_EMAIL = ''

SESSION_COOKIE_SECURE = False
ALLOWED_HOSTS = ['.dragonfly.co.nz']
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')
BROWSERID_AUDIENCES = ['https://songscape-staging.dragonfly.co.nz',]

# generate this per server, and add to debconf
# python -c 'import random; print "".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for i in range(50)])'
SECRET_KEY = '1^8)k29v9fm)=oy1exyl_#cnr0mw=^mx@j()5rshb+*b(70fbg'
#SECRET_KEY = 'qv3^mi)r9t3eeeyrq-ohch8r^7v%*(cfxvl9)6kxbrd9dz=+ek'
