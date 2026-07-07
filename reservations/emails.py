from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse


def notify_family_head_of_request(request, reservation_request):
    """Email the head of the family about a newly submitted request."""
    family = reservation_request.family
    if not family or not family.head_account.email:
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
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [family.head_account.email],
        fail_silently=True,
    )
