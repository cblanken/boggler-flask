#!/bin/sh
poetry run gunicorn --bind 0.0.0.0:5000 --worker-class eventlet --workers 1 --threads 100 main:app
