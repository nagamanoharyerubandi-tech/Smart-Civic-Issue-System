import logging
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification

logger = logging.getLogger(__name__)


def send_civic_notification(
    recipient,
    title,
    message,
    notification_type='general',
    complaint=None,
    action_url='',
    send_email_copy=True
):
    """
    Creates an in-app Notification record and optionally sends an email notification.
    Safe and non-blocking: mail errors are caught and logged.
    """
    try:
        # Create in-app notification
        notification = Notification.objects.create(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=notification_type,
            complaint=complaint,
            action_url=action_url
        )
    except Exception as e:
        logger.error(f"Failed to create in-app notification for {recipient.username}: {e}")
        notification = None

    # Send email notification if user has an email and send_email_copy is True
    if send_email_copy and recipient.email:
        try:
            subject = f"[Smart Civic System] {title}"
            body = (
                f"Dear {recipient.get_full_name() or recipient.username},\n\n"
                f"{message}\n\n"
            )
            if complaint:
                body += f"Complaint Reference ID: {complaint.reference_id}\n"
                body += f"Title: {complaint.title}\n"
                body += f"Status: {complaint.status}\n\n"

            body += (
                "You can view complete updates by logging into the Smart Civic Portal.\n\n"
                "Regards,\n"
                "Civic Administration & Resolution Team\n"
                "Smart Civic Issue Reporting & Resolution Management System"
            )

            send_mail(
                subject=subject,
                message=body,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'support@smartcivic.local'),
                recipient_list=[recipient.email],
                fail_silently=True,
            )
        except Exception as e:
            logger.warning(f"Could not send email notification to {recipient.email}: {e}")

    return notification
