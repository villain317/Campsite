from django.conf import settings
from django.db import models


class Profile(models.Model):
    """Extra per-user info not covered by Django's built-in User model."""

    NOTIFY_OWN_FAMILY = "own_family"
    NOTIFY_ALL = "all"
    NOTIFY_NONE = "none"
    NOTIFICATION_CHOICES = [
        (NOTIFY_OWN_FAMILY, "Only requests from my own family"),
        (NOTIFY_ALL, "All requests, from any family"),
        (NOTIFY_NONE, "Don't email me about requests"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    avatar = models.ImageField(upload_to="avatars/%Y/%m/", blank=True, null=True)
    notification_preference = models.CharField(
        max_length=20,
        choices=NOTIFICATION_CHOICES,
        default=NOTIFY_OWN_FAMILY,
        help_text="Which new-request emails you'd like to receive, if you're an approver.",
    )

    def __str__(self):
        return f"Profile for {self.user}"
