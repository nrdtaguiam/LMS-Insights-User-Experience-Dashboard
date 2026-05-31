from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "lms_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Optional: Add beat schedule here if running celery beat
celery_app.conf.beat_schedule = {
    'fetch-users-every-hour': {
        'task': 'app.worker.tasks.task_fetch_users',
        'schedule': 3600.0,
    },
    'fetch-courses-every-hour': {
        'task': 'app.worker.tasks.task_fetch_courses',
        'schedule': 3600.0,
    },
}
