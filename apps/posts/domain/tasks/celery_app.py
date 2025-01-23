from datetime import UTC, datetime, timedelta
from celery import Celery
from celery.schedules import crontab
from apps.posts.domain.service import list_recommended_posts_instance
from sqlmodel import Session
from email.message import EmailMessage
from config import SENDGRID_POST_RECOMMENDATION_API_KEY,FROM_EMAIL,SENDGRID_TEMPLATE_POST_RECOMMENDATION
from apps.posts.domain.models import Posts
from apps.posts.domain.service import list_recommended_posts_instance
from apps.user.domain.service import get_current_user
from database import SessionDep,engine
from sqlmodel import select
from apps.user.domain.models import Users,Profile
from sendgrid.helpers.mail import Mail
from sendgrid import SendGridAPIClient
from sqlalchemy.orm import sessionmaker

celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)

celery_app.conf.beat_schedule = {
    "run-periodic-task-every-20-seconds":{
        "task": "apps.posts.domain.tasks.celery_app.send_post_recommendation_email", 
        "schedule":20.0,
    },   
}

celery_app.conf.update(woker_pool = 'solo')

celery_app.autodiscover_tasks(
    ["apps.posts.domain.tasks.celery_app.send_post_recommendation_email"]
)

celery_app.conf.timezone = "Asia/Kolkata"

def serialize_posts(posts:list[Posts]):
    """
    Converts a list of Posts objects to a list of dictionaries.
    """
    return [
        {
            "title": post.title,
            "content": post.content,
            "file_url": post.file_url
        }
        for post in posts
    ]

@celery_app.task
def send_post_recommendation_email():
    """
    Celery function to send email notification to user regarding their post removal
    """
    with Session(engine) as session:
        query = select(Profile)
        users_to_send_email = session.exec(query).all()
            
        for i in users_to_send_email:
            recommended_posts = list_recommended_posts_instance(session,i.user)
            serialized_posts = serialize_posts(recommended_posts)
            print(serialized_posts)
            message = Mail(
                from_email=FROM_EMAIL,
                to_emails= i.user.email,
                subject="Your Daily Recommended Posts",
            )
            message.dynamic_template_data = {
                "posts" : serialized_posts,
            }
            message.template_id = SENDGRID_TEMPLATE_POST_RECOMMENDATION
            try:
                print("SENDGRID_API_KEY:", SENDGRID_POST_RECOMMENDATION_API_KEY)
                sg = SendGridAPIClient(SENDGRID_POST_RECOMMENDATION_API_KEY)
                response = sg.send(message)
                print(f"Email sent successfully! Status code: {response.status_code}")
                print(response.body)
            except Exception as e:
                print(f"Error sending email: {e}")



