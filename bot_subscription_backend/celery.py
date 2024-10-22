from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot_subscription_backend.settings')

app = Celery('bot_subscription_backend')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Automatically discover tasks from all installed apps in Django.
app.autodiscover_tasks()

# Configure Celery to use the django-celery-beat scheduler
app.conf.beat_scheduler = 'django_celery_beat.schedulers.DatabaseScheduler'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

