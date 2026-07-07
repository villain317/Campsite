from django import forms

from .models import Checklist


class ChecklistForm(forms.ModelForm):
    class Meta:
        model = Checklist
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. Short Leave Checklist"}
            ),
        }
