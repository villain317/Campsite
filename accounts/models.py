from django.conf import settings
from django.db import models


class Profile(models.Model):
    """Extra per-user info not covered by Django's built-in User model."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    avatar = models.ImageField(upload_to="avatars/%Y/%m/", blank=True, null=True)

    def __str__(self):
        return f"Profile for {self.user}"
