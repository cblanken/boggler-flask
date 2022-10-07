"""Entrypoint module for starting app and loading configurations
"""
from werkzeug.middleware.proxy_fix import ProxyFix
from app import create_app
from app.board import bp

# Create base app object
app = create_app()
app.register_blueprint(bp)

# Apply configurations
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
