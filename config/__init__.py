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

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    INIT_DB = os.environ.get("INIT_DB")
    SQLITE_DB = os.environ.get("SQLITE_DB") or "app/db/boggler.sqlite"


class ProductionConfig(Config):
    DEBUG = False
    INIT_DB = os.environ.get("INIT_DB")
    SQLITE_DB = os.environ.get("SQLITE_DB") or "app/db/boggler.sqlite"

    @classmethod
    def init_app(cls, app):
        if cls.SQLITE_DB is None:
            print(
                "Incomplete configuration. A sqlite database file must be provided via the SQLITE_DB variable.",
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
