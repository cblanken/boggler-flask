#!/bin/sh

source venv/bin/activate
celery -A celery_worker.cel worker -E -P threads &
exec gunicorn --bind 0.0.0.0:5000 --workers 4 --access-logfile - --error-logfile - main:app
