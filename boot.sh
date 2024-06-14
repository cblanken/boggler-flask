#!/bin/sh
poetry run gunicorn --bind 0.0.0.0:5000 --workers 4 --threads 50 --access-logfile - --error-logfile - main:app
