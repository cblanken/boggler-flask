"""Entrypoint module for starting app and loading configurations
"""

from os import getenv
from app import create_app
from app.board import bp

# Create base app object
app = create_app(getenv("FLASK_CONFIG") or "default")
app.register_blueprint(bp)

if __name__ == "__main__":
    app.socketio.run(host="0.0.0.0")
