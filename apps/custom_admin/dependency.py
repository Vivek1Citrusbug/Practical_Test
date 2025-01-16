import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from config import FROM_EMAIL,POST_REMOVED_TEMPLATE_ID,POST_REMOVED_SENDGRID_KEY
from datetime import datetime

def send_post_removal_email(user_email:str,user_name:str, post_title:str, removal_reason:str | None = None, support_url:str | None = None):
    """
    Dependency function to send email notification to user regarding their post removal
    """
    
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=user_email,
        subject='Notification: Your Post Has Been Removed',
    )
    current_year = datetime.now().year
    message.dynamic_template_data = {
        "user_name": user_name,
        "post_title": post_title,
        "removal_reason": removal_reason,
        "support_url": support_url,
        "current_year": current_year
    }
    message.template_id = POST_REMOVED_TEMPLATE_ID  
    try:
        print("SENDGRID_API_KEY:", POST_REMOVED_SENDGRID_KEY)
        sg = SendGridAPIClient(POST_REMOVED_SENDGRID_KEY)
        response = sg.send(message)
        print(f"Email sent successfully! Status code: {response.status_code}")
        print(response.body)
    except Exception as e:
        print(f"Error sending email: {e}")
