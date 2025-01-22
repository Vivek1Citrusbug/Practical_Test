##############################################################################################
######## Recurring task for giving recommendation to user for everyday at 10:00 AM UST #######
##############################################################################################

from apps.posts.domain.tasks.celery_app import app
from email.message import EmailMessage
from config import (
    FROM_EMAIL,
    SENDGRID_POST_RECOMMENDATION_API_KEY,
    SENDGRID_TEMPLATE_POST_RECOMMENDATION
)
from sendgrid.helpers.mail import Mail
from datetime import datetime
from sendgrid import SendGridAPIClient


@celery_app.task
def send_recommended_posts_email(user_email: str, posts: list):
    # Format the email content
    subject = "Your Daily Recommended Posts"
    body = "Here are your recommended posts:\n\n" + "\n".join(posts)

    # Use an email library to send the email
    send_email(to=user_email, subject=subject, body=body)

    return f"Email sent to {user_email} at {datetime.utcnow()}"


@app.task
def send_post_removal_email(
    user_email: str,
    user_name: str,
    post_title: str,
    removal_reason: str | None = None,
    support_url: str | None = None,
):
    """
    Dependency function to send email notification to user regarding their post removal
    """

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=user_email,
        subject="Your Daily Recommended Posts",
    )
    current_year = datetime.now().year
    message.dynamic_template_data = {
        "user_name": user_name,
        "post_title": post_title,
        "removal_reason": removal_reason,
        "support_url": support_url,
        "current_year": current_year,
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


# Configure periodic tasks
app.conf.beat_schedule = {
    "run-periodic-task-every-20-seconds": {
        "task": "tasks.task_2_celery.send_email_celery",
        "schedule": 20.0,
        "args": (),
    },
}

app.conf.timezone = "Asia/Kolkata"
