from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'robinboardAPI.settings')

app = Celery('robinboardAPI')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Other Celery settings
app.conf.beat_schedule = {
    'processOutstandingCredits': {
        'task': 'billing.tasks.processOutstandingCredits',
        'schedule': crontab(minute=0, hour=0),
        # 'args': (*args)
    },
    'processBilling': {
        'task': 'billing.tasks.processBilling',
        'schedule': crontab(minute=0, hour=3),
        # 'args': (*args)
    }
}

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
