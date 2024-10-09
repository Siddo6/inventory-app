from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Initialize Celery
app = Celery('config')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks from all installed apps
app.autodiscover_tasks()
app.conf.update(
    broker_connection_retry_on_startup=True  # Add this line
)
# Celery Beat Schedule to run on the 1st of every month
app.conf.beat_schedule = {
    'save-monthly-data-every-hour-on-first-day': {
        'task': 'product.tasks.save_monthly_data',
        'schedule': crontab(minute=0, hour='*', day_of_month='1'),  # Runs every hour on the 1st day of the month
    },
}
