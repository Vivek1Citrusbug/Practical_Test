from celery import Celery
from celery.schedules import crontab


app = Celery("tasks", broker="redis://localhost:6379/0", backend='redis://localhost:6379/0')


# # Configure periodic tasks
# app.conf.beat_schedule = {
#     "run-periodic-task-every-20-seconds": {
#         "task": "tasks.task_post_recommendation",
#         "schedule": 20.0,
#         "args": (),
#     },
# }

app.conf.timezone = "Asia/Kolkata"