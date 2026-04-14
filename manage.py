#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import threading
import webbrowser


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'root.settings')
    
    open_browser = False
    if len(sys.argv) == 1:
        sys.argv += ["runserver", "127.0.0.1:8000"]
        open_browser = True
    elif len(sys.argv) > 1 and sys.argv[1] == 'runserver':
        open_browser = True

    if getattr(sys, 'frozen', False):
        # Dans l'exécutable PyInstaller, Django autoreload échoue car il ne trouve pas
        # le script enfant. On désactive donc le reloader automatiquement.
        if len(sys.argv) > 1 and sys.argv[1] == 'runserver' and '--noreload' not in sys.argv:
            sys.argv.append('--noreload')

    if open_browser:
        threading.Timer(1.5, lambda: webbrowser.open('http://127.0.0.1:8000')).start()

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
