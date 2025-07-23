# utils.py

import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.core.mail import BadHeaderError

logger = logging.getLogger(__name__)

def send_notification_email(subject, recipient_list, context, email_template):
    try:
      # Render the HTML content using the template
        html_content = render_to_string(email_template, context)
        text_content = strip_tags(html_content)  # Create a plain text version

        # Create the email
        email = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,  # From email
            recipient_list
        )
        email.attach_alternative(html_content, "text/html")  # Attach the HTML content

        # Send the email
        email.send(fail_silently=False)

    except BadHeaderError:
        logger.error("Invalid header found.")
    except Exception as e:
        logger.error(f"Error sending email: {e}")

