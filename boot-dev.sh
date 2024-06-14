#!/bin/sh
poetry run celery -A celery_worker.cel worker -E -P threads &
poetry run flask --app main --debug run
