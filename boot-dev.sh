#!/bin/sh
source venv/bin/activate
celery -A celery_worker.cel worker -E -P threads &
flask --app main --debug run
