from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from django.urls import reverse
from .models import ApprovalRequest
from notifications.utils import send_notification_email  # Import the email function


@receiver(post_save, sender=ApprovalRequest)
def approval_request_created(sender, instance, created, **kwargs):
  if created:  # Only send notification when a new approval is created
    # Get the user's profile
    profile = instance.created_by.userprofile
    subject = f'Approval Request New Document Submitted: {instance.title}'
    # Build the approval link
    approval_link = f"{settings.BASE_URL}{reverse('approval_list')}"
    logo_url = f"{settings.BASE_URL}{settings.STATIC_URL}img/Logo_lupien_UHN_P2CC_2025.png"  # Ensure BASE_URL is set correctly
    context = {
      'approver_name': profile.lab.supervisor,
      'request_type': 'Approve Sequence request',
      'request_title': instance.title,
      'requester_name': instance.created_by.username,
      'approval_link': approval_link,
      'logo_url': logo_url,
    }
    # TODO needs to also add the submitter and add Ankita email address (ankita.nand@uhn.ca)
    recipient_list = [profile.lab.supervisor]
    send_notification_email(subject, recipient_list, context, 'approval_request_created_email_template.html')

@receiver(post_save, sender=ApprovalRequest)
def approval_request_processed(sender, instance, created, **kwargs):
  # TODO add comment to email for disapprove
  if instance.status != 'pending':  # Only send notification when approved or disapproved
    subject = f'Document {instance.status}: {instance.title}'

    # Build the approval link
    approval_link = f"{settings.BASE_URL}{reverse('approval_list')}"
    logo_url = f"{settings.BASE_URL}{settings.STATIC_URL}img/Logo_lupien_UHN_P2CC_2025.png"  # Ensure BASE_URL is set correctly
    context = {
      'requester_name': instance.created_by.username,
      'request_title': instance.title,
      'approver_name': instance.approved_by.username,
      'result': instance.status,
      'approval_link': approval_link,
      'logo_url': logo_url,
    }
    # TODO send to supervisor submitter and Ankita
    recipient_list = [instance.created_by.email]
    send_notification_email(subject, recipient_list, context, 'approval_request_processed_email_template.html')



