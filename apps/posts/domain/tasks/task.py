##############################################################################################
######## Recurring task for giving recommendation to user for everyday at 10:00 AM UST #######
##############################################################################################

from apps.posts.domain.tasks.celery_app import celery_app as celery_application
from email.message import EmailMessage
from sendgrid.helpers.mail import Mail
from datetime import datetime
from sendgrid import SendGridAPIClient
from apps.posts.domain.models import Posts
from service import list_recommended_posts_instance
from database import SessionDep
from user.domain.service import get_current_user
from user.domain.models import Users
from config import SENDGRID_POST_RECOMMENDATION_API_KEY,FROM_EMAIL,SENDGRID_TEMPLATE_POST_RECOMMENDATION



@celery_application.task
def send_post_recommendation_email(
    user:Users,
    session:SessionDep
):
    """
    Celery function to send email notification to user regarding their post removal
    """

    recommended_posts = list_recommended_posts_instance(session,user)
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=user.email,
        subject="Your Daily Recommended Posts",
    )
    message.dynamic_template_data = {
        "posts": recommended_posts,
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


