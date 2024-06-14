"""Config layer to apply configurations based on environment type"""

import sys
import os
import secrets
import string
from werkzeug.middleware.proxy_fix import ProxyFix


def get_secret():
    """Generate random alphanumeric secret"""
    return "".join(
        secrets.choice(string.ascii_letters + string.digits) for _ in range(32)
    )


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or get_secret()
    SQLALCHEMY_TRACK_MODIFICATION = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    DB_HOST = os.environ.get("DEV_DB_HOST") or "localhost"
    DB_PORT = os.environ.get("DEV_DB_PORT") or "5555"
    DB_USER = os.environ.get("DEV_DB_USER") or "postgres"
    DB_PASS = os.environ.get("DEV_DB_PASS") or "password"
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/boggler?connect_timeout=10"


class ProductionConfig(Config):
    DEBUG = False
    DB_HOST = os.environ.get("PROD_DB_HOST") or "localhost"
    DB_PORT = os.environ.get("PROD_DB_PORT") or "5555"
    DB_USER = os.environ.get("PROD_DB_USER") or "postgres"
    DB_PASS = os.environ.get("PROD_DB_PASS") or "password"
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/boggler?connect_timeout=10"

    @classmethod
    def init_app(cls, app):
        if cls.DB_USER is None or cls.DB_PASS is None:
            print(
                "Incomplete configuration. A database username and password must be provided via the PROD_DB_USER and PROD_DB_PASS environment variables",
                file=sys.stderr,
            )
            sys.exit()

        Config.init_app(app)
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
