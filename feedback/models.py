from django.conf import settings
from django.db import models


class FeedbackItem(models.Model):
    """Feedback, a feature request, or a bug report submitted by a user."""

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="feedback_items"
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Feedback from {self.author} ({self.created_at:%Y-%m-%d})"
