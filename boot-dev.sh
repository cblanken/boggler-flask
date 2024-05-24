#!/bin/sh
celery -A celery_worker.cel worker -E -P threads &
flask --app main --debug run
