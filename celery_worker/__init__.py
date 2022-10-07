"""App instance for celery worker
"""
from celery import Celery
from app import create_app
def create_celery():
    """Configure Celery object for async tasks
    """
    cel = Celery("boggler-celery",
        broker="redis://127.0.0.1:6379/0",
        backend="redis://127.0.0.1:6379/0",
        include="app.board"
    )

    return cel

app = create_app()
cel = create_celery()
