"""Config layer to apply configurations based on environment type"""

import sys
import os
import secrets
import string
from werkzeug.middleware.proxy_fix import ProxyFix
from pathlib import Path


def get_secret():
    """Generate random alphanumeric secret"""
    return "".join(
        secrets.choice(string.ascii_letters + string.digits) for _ in range(32)
    )


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", get_secret())
    DATA_DIR = Path(os.environ.get("DATA_DIR", "data"))

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    INIT_DB = os.environ.get("INIT_DB")


class ProductionConfig(Config):
    DEBUG = False
    INIT_DB = os.environ.get("INIT_DB")

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
