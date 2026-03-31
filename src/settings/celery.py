import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")
app = Celery("settings")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

app.conf.beat_schedule = {
    "background_email_check": {
        "task": "emails.tasks.bg_emails",
        "schedule": crontab(minute="*/30"),
    },
}
