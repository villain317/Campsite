from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse

hex_color_validator = RegexValidator(
    regex=r"^#[0-9A-Fa-f]{6}$",
    message="Enter a valid hex color, e.g. #3366CC",
)


class Family(models.Model):
    """One of the three sibling families that share Oakholm."""

    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(
        max_length=7,
        validators=[hex_color_validator],
        help_text="Hex color used to represent this family on the calendar, e.g. #3366CC",
    )
    head_account = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="family_headed",
        help_text="The account for the head of this family. This account can approve or deny requests.",
    )

    class Meta:
        verbose_name_plural = "families"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Household(models.Model):
    """A group of people within a family who usually attend together."""

    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="households")
    name = models.CharField(max_length=100, help_text="e.g. 'Mike & Sarah' or 'Grandma & Grandpa'")

    class Meta:
        ordering = ["family__name", "name"]

    def __str__(self):
        return f"{self.name} ({self.family.name})"


class Person(models.Model):
    """A member of one of the families. May or may not have a login account."""

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="members")
    household = models.ForeignKey(
        Household,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members",
        help_text="Optional: the household this person belongs to, for grouping on the request form.",
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="person_profile",
        help_text="Optional: the account tied to this person, if they have one.",
    )

    class Meta:
        verbose_name_plural = "people"
        ordering = ["family__name", "last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.family.name})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def clean(self):
        if self.household_id and self.household.family_id != self.family_id:
            raise ValidationError("Household must belong to the same family as this person.")


class ReservationRequest(models.Model):
    """A request to use Oakholm for a range of dates."""

    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_DENIED = "denied"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_DENIED, "Denied"),
    ]

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservation_requests",
    )
    people = models.ManyToManyField(
        Person,
        related_name="reservation_requests",
        help_text="Everyone who will be staying at Oakholm for this request.",
    )
    estimated_occupants = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    requested_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="decided_requests",
    )
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["start_date"]

    def __str__(self):
        return f"{self.requested_by} - {self.start_date} to {self.end_date} ({self.status})"

    def clean(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError("End date must be on or after the start date.")

    def get_absolute_url(self):
        return reverse("reservations:approve_list")

    @property
    def family(self):
        """The family this request belongs to, derived via person records.

        Preference order: the family of the Person tied to the requester's
        account, then the family of the first attendee.
        """
        person = Person.objects.filter(user=self.requested_by).first()
        if person:
            return person.family
        first_attendee = self.people.first()
        return first_attendee.family if first_attendee else None

    def overlapping_requests(self):
        """Other pending/approved requests whose date range overlaps this one."""
        return (
            ReservationRequest.objects.filter(
                status__in=[self.STATUS_PENDING, self.STATUS_APPROVED],
                start_date__lte=self.end_date,
                end_date__gte=self.start_date,
            )
            .exclude(pk=self.pk)
            .select_related("requested_by")
        )
