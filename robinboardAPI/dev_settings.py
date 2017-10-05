# Start with our base settings
from .settings import *
DEBUG=True
CELERY_BROKER_URL = 'amqp://localhost'

# DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.postgresql',
#             'NAME': "djangorest",
#             'USER': "robinboardDev",
#             'PASSWORD': os.environ['RDS_PASSWORD'],
#             'HOST': "robinboard-dev.cng93thgqnqn.us-east-1.rds.amazonaws.com",
#             'PORT': "5432",
#         }
# }

from celery.schedules import crontab
# Other Celery settings
CELERY_BEAT_SCHEDULE = {
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
