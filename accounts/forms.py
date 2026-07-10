from django import forms
from django.contrib.auth import get_user_model

from reservations.models import Person

from .models import Profile

User = get_user_model()


class _BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


class ProfileUserForm(_BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]


class ProfileAvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["avatar"]
        widgets = {
            "avatar": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


class ProfileNotificationForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["notification_preference"]
        widgets = {
            "notification_preference": forms.RadioSelect,
        }


class CreateAccountForm(forms.Form):
    person = forms.ModelChoiceField(
        queryset=Person.objects.none(),
        widget=forms.Select(attrs={"class": "form-select"}),
        help_text="Only people who don't already have a login are listed.",
    )
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))
    is_approver = forms.BooleanField(
        required=False,
        label="Add to Approvers group (can approve/deny requests)",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["person"].queryset = (
            Person.objects.filter(user__isnull=True)
            .select_related("family")
            .order_by("family__name", "last_name", "first_name")
        )
