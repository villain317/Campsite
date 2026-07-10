from django import forms

from .models import Person, ReservationRequest


class ReservationRequestForm(forms.ModelForm):
    start_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}))

    class Meta:
        model = ReservationRequest
        fields = ["start_date", "end_date", "people", "estimated_occupants"]
        widgets = {
            "people": forms.CheckboxSelectMultiple,
            "estimated_occupants": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.requester_person = Person.objects.filter(user=user).first() if user else None

        # Show everyone, from every family - the "Who's coming?" section of
        # the template renders these grouped by family/household itself, so
        # this queryset just needs to be complete and valid for validation.
        self.fields["people"].queryset = Person.objects.select_related("family", "household").order_by(
            "family__name", "last_name", "first_name"
        )

        if self.requester_person and not self.is_bound and not self.instance.pk:
            self.fields["people"].initial = [self.requester_person.pk]

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if start_date and end_date and end_date < start_date:
            self.add_error("end_date", "End date must be on or after the start date.")
        return cleaned_data
