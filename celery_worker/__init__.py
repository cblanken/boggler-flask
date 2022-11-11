"""App instance for celery worker
"""
from celery import Celery
from flask import Flask
from config import config

app = Flask(__name__)
cfg = config["celery"]
app.config.from_object(cfg)
cfg.init_app(app)
cel = cfg.create_celery()
