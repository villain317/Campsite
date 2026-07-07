from django import forms

from .models import Note


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(
                attrs={"class": "form-control", "rows": 4, "placeholder": "Leave a note..."}
            ),
        }
