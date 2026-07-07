import datetime

from django.conf import settings
from django.db import models
from django.utils import timezone

AUTO_ARCHIVE_AFTER = datetime.timedelta(days=365)


class Note(models.Model):
    """A free-form note left by a family member."""

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notes"
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Note by {self.author} ({self.created_at:%Y-%m-%d})"

    @property
    def is_effectively_archived(self):
        """True if manually archived, or automatically aged out after a year."""
        if self.is_archived:
            return True
        return timezone.now() - self.created_at >= AUTO_ARCHIVE_AFTER

    @property
    def auto_archive_date(self):
        return self.created_at + AUTO_ARCHIVE_AFTER


class NoteImage(models.Model):
    """A photo attached to a note."""

    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="note_images/%Y/%m/")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["uploaded_at"]

    def __str__(self):
        return f"Image for {self.note}"
