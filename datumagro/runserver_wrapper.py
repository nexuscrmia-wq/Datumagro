"""
Runserver wrapper to start Django dev server from inside the package directory
This avoids relying on an external manage.py when running inside the workspace.
"""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'datumagro.settings')

if __name__ == '__main__':
    # Ensure parent directory is on sys.path so Django can import apps if needed
    here = os.path.dirname(os.path.abspath(__file__))
    parent = os.path.dirname(here)
    if parent not in sys.path:
        sys.path.insert(0, parent)

    from django.core.management import execute_from_command_line

    execute_from_command_line(['manage.py', 'runserver', '127.0.0.1:8000'])
