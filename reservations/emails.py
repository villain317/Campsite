from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.urls import reverse

from .utils import is_approver

User = get_user_model()


def _recipients_for_request(reservation_request):
    """Everyone who should be emailed about a new request, respecting each
    approver's notification preference.

    - "own_family" (the default): only if this request belongs to the
      family they head.
    - "all": every request, regardless of family.
    - "none": never.
    """
    from accounts.models import Profile

    family = reservation_request.family
    candidates = User.objects.select_related("profile", "family_headed")

    recipients = []
    for user in candidates:
        if not user.email or not is_approver(user):
            continue

        profile = getattr(user, "profile", None)
        preference = profile.notification_preference if profile else Profile.NOTIFY_OWN_FAMILY

        if preference == Profile.NOTIFY_NONE:
            continue
        if preference == Profile.NOTIFY_ALL:
            recipients.append(user.email)
            continue

        # own_family: only notify if this request belongs to the family they head.
        own_family = getattr(user, "family_headed", None)
        if own_family and family and own_family.pk == family.pk:
            recipients.append(user.email)

    return recipients


def notify_approvers_of_request(request, reservation_request):
    """Email everyone eligible to approve/deny about a newly submitted request."""
    recipients = _recipients_for_request(reservation_request)
    if not recipients:
        return

    requester_name = reservation_request.requested_by.get_full_name() or reservation_request.requested_by.username
    approve_url = request.build_absolute_uri(reverse("reservations:approve_list"))
    subject = f"New Oakholm request from {requester_name}"
    message = (
        f"{requester_name} has requested Oakholm.\n\n"
        f"Dates: {reservation_request.start_date} to {reservation_request.end_date}\n"
        f"Estimated occupants: {reservation_request.estimated_occupants}\n"
        f"Attendees: {', '.join(p.full_name for p in reservation_request.people.all())}\n\n"
        f"Log in to review and approve or deny this request:\n{approve_url}"
    )
    # Send individually rather than as one multi-recipient email so
    # approvers don't see each other's addresses.
    for email in recipients:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=True,
        )
