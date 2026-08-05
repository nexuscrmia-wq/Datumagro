# datumagro/wsgi.py

import os
import mimetypes
from django.core.wsgi import get_wsgi_application

mimetypes.add_type('application/vnd.android.package-archive', '.apk')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'datumagro.settings')

application = get_wsgi_application()