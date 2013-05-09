"""
WSGI config for songscape.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.
"""
import os
import sys
sys.path.append('/var/www/django/songscape/')
# We should standardise to include/exclude the project path (i.e. www/) rather than
# keep both in the path
sys.path.append('/var/www/django/songscape/www')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "www.settings")

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Apply WSGI middleware here.
# from helloworld.wsgi import HelloWorldApplication
# application = HelloWorldApplication(application)
