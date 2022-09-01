import os
from celery import Celery

def make_celery(app_name=__name__):
    backend = os.getenv('CELERY_RESULT_BACKEND')
    broker = os.getenv('BROKER_URL')
    return Celery(app_name, backend=backend, broker=broker)

celery = make_celery()