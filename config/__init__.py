"""Config layer to apply configurations based on environment type"""
import os
import secrets
import string
from celery import Celery
from werkzeug.middleware.proxy_fix import ProxyFix

def get_secret():
    """Generate random alphanumeric secret"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or get_secret()

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        app.wsgi_app = ProxyFix(
            app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
        )

class CeleryConfig(Config):
    @staticmethod
    def create_celery():
        return Celery("boggler-celery",
            broker="redis://redis:6379/0",
            backend="redis://redis:6379/0",
            include="app.board"
        )

config = {
    "celery": CeleryConfig,
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
