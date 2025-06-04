from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import ApprovalRequest
from notifications.utils import send_notification_email  # Import the email function


@receiver(post_save, sender=ApprovalRequest)
def approval_request_created(sender, instance, created, **kwargs):
  if created:  # Only send notification when a new approval is created
    # Get the user's profile
    profile = instance.created_by.userprofile
    subject = f'New Document Submitted: {instance.title}'
    message = (
        f'Hello "{profile.lab.supervisor}",\n\n'
        f'A new document titled "{instance.title}" has been submitted by {instance.created_by.username}.\n'
        f'You can review it in the system.'
    )
    recipient_list = [profile.lab.supervisor]
    send_notification_email(subject, message, recipient_list)

@receiver(post_save, sender=ApprovalRequest)
def approval_request_processed(sender, instance, created, **kwargs):
  if instance.status != 'pending':  # Only send notification when approved or disapproved
    subject = f'Document {instance.status}: {instance.title}'
    message = (
        f'Hello {instance.created_by.username},\n\n'
        f'Your document "{instance.title}" has been '
        f'{instance.status} by {instance.approved_by.username}.\n'
    )

    recipient_list = [instance.created_by.email]
    send_notification_email(subject, message, recipient_list)



