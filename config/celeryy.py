"""Module for celery instance for 'top_api' project."""
from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery(
    "config",
    broker="redis://localhost:6379",
    backend="redis://localhost:6379",
    include=["vpn_app.tasks"],
)

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
