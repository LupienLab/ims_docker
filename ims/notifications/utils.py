# utils.py

import logging
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import BadHeaderError

logger = logging.getLogger(__name__)

def send_notification_email(subject, message, recipient_list):
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,  # From email
            recipient_list,
            fail_silently=False,
        )
    except BadHeaderError:
        logger.error("Invalid header found.")
    except Exception as e:
        logger.error(f"Error sending email: {e}")

