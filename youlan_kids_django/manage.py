#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# 在DJANGO_SETTINGS_MODULE前添加编码配置
if __name__ == "__main__":
    os.environ.setdefault("PYTHONUTF8", "1")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "youlan_kids_django.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
