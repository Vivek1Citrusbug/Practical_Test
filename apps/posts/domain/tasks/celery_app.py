from celery import Celery
from celery.schedules import crontab


app = Celery("tasks", broker="redis://localhost:6379/0", backend='redis://localhost:6379/0')


# Configure periodic tasks
app.conf.beat_schedule = {
    "run-periodic-task-every-24-hours": {
        "task": "tasks.task_2_celery.send_email_celery",
        "schedule": 60, # schedule task everyday at every minute to check functionality working or not.
    },
}

app.conf.timezone = "Asia/Kolkata"