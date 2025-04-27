#!/bin/sh
export FLASK_CONFIG=production
poetry run gunicorn --bind 0.0.0.0:5000 --worker-class eventlet --workers 4 --threads 100 main:app
