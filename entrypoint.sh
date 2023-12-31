#!/bin/bash

alembic upgrade head
if [ $FLASK_ENV = "development" ]
then
    echo "ambiente ${FLASK_ENV}: eliminando crontab"
    celery -A worker.celery worker --loglevel=DEBUG -D -f /var/log/celery.log
    gunicorn -w $WORKERS --bind 0.0.0.0:5000 --reload --access-logfile '-' 'wsgi:create_app()'

else
    echo $FLASK_ENV
    celery -A worker.celery worker --loglevel=DEBUG -D -f /var/log/celery.log
    gunicorn -w $WORKERS --bind 0.0.0.0:5000 --access-logfile '-' 'wsgi:create_app()'
fi