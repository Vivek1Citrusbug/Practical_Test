##############################################################################################
######## Recurring task for giving recommendation to user for everyday at 10:00 AM UST #######
##############################################################################################

from tasks.celery_app import app
from email.message import EmailMessage
from config import SENDGRID_POST_RECOMMENDATION_API_KEY,FROM_EMAIL,SENDGRID_TEMPLATE_POST_RECOMMENDATION
from sendgrid.helpers.mail import Mail
from datetime import datetime
from sendgrid import SendGridAPIClient
from apps.posts.domain.models import Posts
from apps.posts.domain.service import list_recommended_posts_instance
from database import SessionDep
from apps.user.domain.service import get_current_user

@app.task(name="tasks.send_recommendation_email")
def send_post_recommendation_email(
    user_email: str,
    session:SessionDep
):
    """
    Celery function to send email notification to user regarding their post removal
    """

    recommended_posts = list_recommended_posts_instance(session)
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=user_email,
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


