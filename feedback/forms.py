from django import forms

from .models import FeedbackItem


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = FeedbackItem
        fields = ["message"]
        widgets = {
            "message": forms.Textarea(
                attrs={"class": "form-control", "rows": 6, "placeholder": "What's on your mind?"}
            ),
        }
