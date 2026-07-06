from django import forms

from .models import Person, ReservationRequest


class ReservationRequestForm(forms.ModelForm):
    start_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}))

    class Meta:
        model = ReservationRequest
        fields = ["start_date", "end_date", "people", "estimated_occupants"]
        widgets = {
            "people": forms.SelectMultiple(attrs={"class": "form-select", "size": 8}),
            "estimated_occupants": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.requester_person = Person.objects.filter(user=user).first() if user else None

        if self.requester_person:
            # Scope the attendee choices to the requester's own family.
            self.fields["people"].queryset = Person.objects.filter(
                family=self.requester_person.family
            ).order_by("last_name", "first_name")
            if not self.is_bound:
                self.fields["people"].initial = [self.requester_person.pk]
        else:
            # No person tied to this account yet - fall back to showing everyone.
            self.fields["people"].queryset = Person.objects.order_by(
                "family__name", "last_name", "first_name"
            )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if start_date and end_date and end_date < start_date:
            self.add_error("end_date", "End date must be on or after the start date.")
        return cleaned_data
