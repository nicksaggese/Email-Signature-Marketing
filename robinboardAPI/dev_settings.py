# Start with our base settings
from .settings import *
DEBUG=True


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


CELERY_BROKER_URL = 'amqp://localhost'
