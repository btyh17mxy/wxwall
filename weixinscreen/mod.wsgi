
import os
import sys

sys.path.append('/www/wxwall')
os.environ["DJANGO_SETTINGS_MODULE"] = 'wxwall.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

