from django.conf import settings
from django.db import models
from django.db.models import Q


class Checklist(models.Model):
    """A checklist template, e.g. 'Short Leave Checklist'."""

    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ChecklistItem(models.Model):
    """A single item belonging to a checklist template."""

    checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self):
        return f"{self.name} ({self.checklist.name})"


class ChecklistRun(models.Model):
    """One person's pass at filling out a checklist (in progress or completed)."""

    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = [
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_COMPLETED, "Completed"),
    ]

    checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE, related_name="runs")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="checklist_runs"
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_IN_PROGRESS)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-started_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "checklist"],
                condition=Q(status="in_progress"),
                name="one_in_progress_run_per_user_per_checklist",
            )
        ]

    def __str__(self):
        return f"{self.checklist.name} - {self.user} ({self.status})"


class ChecklistRunItem(models.Model):
    """Whether a given item was checked off within a specific run."""

    run = models.ForeignKey(ChecklistRun, on_delete=models.CASCADE, related_name="run_items")
    item = models.ForeignKey(ChecklistItem, on_delete=models.CASCADE, related_name="run_items")
    checked = models.BooleanField(default=False)
    checked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["item__created_at", "item__id"]
        unique_together = ("run", "item")

    def __str__(self):
        return f"{self.item.name} - {'checked' if self.checked else 'unchecked'}"


class ChecklistImage(models.Model):
    """A photo uploaded as part of a checklist run."""

    run = models.ForeignKey(ChecklistRun, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="checklist_images/%Y/%m/")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["uploaded_at"]

    def __str__(self):
        return f"Image for {self.run}"
