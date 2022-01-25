#!/bin/bash

alembic upgrade head
if [ $FLASK_ENV = "development" ]
then
    echo "ambiente ${FLASK_ENV}: eliminando crontab"
    gunicorn -w $WORKERS --timeout 60 --bind 0.0.0.0:5000 --reload --access-logfile '-' 'wsgi:create_app()'
else
    echo $FLASK_ENV
    gunicorn -w $WORKERS --timeout 60 --bind 0.0.0.0:5000 --access-logfile '-' 'wsgi:create_app()'
fi