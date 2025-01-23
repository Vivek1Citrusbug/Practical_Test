from datetime import UTC, datetime, timedelta
from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)

# celery_app.autodiscover_tasks(["tasks.task"])
celery_app.conf.beat_schedule = {}

celery_app.conf.timezone = "Asia/Kolkata"

celery_app.conf.broker_connection_retry_on_startup = True
