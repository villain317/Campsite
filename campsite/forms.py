from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm


class _BootstrapFormMixin:
    """Adds the Bootstrap form-control class to every field's widget."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


class StyledPasswordChangeForm(_BootstrapFormMixin, PasswordChangeForm):
    """Same as Django's PasswordChangeForm, just with Bootstrap classes."""


class StyledPasswordResetForm(_BootstrapFormMixin, PasswordResetForm):
    """Same as Django's PasswordResetForm, just with Bootstrap classes."""


class StyledSetPasswordForm(_BootstrapFormMixin, SetPasswordForm):
    """Same as Django's SetPasswordForm, just with Bootstrap classes."""
