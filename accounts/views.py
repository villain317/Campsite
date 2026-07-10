from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.text import slugify

from .forms import CreateAccountForm, ProfileAvatarForm, ProfileNotificationForm, ProfileUserForm
from .models import Profile

User = get_user_model()


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        user_form = ProfileUserForm(request.POST, instance=request.user)
        avatar_form = ProfileAvatarForm(request.POST, request.FILES, instance=profile)
        notification_form = ProfileNotificationForm(request.POST, instance=profile)
        if user_form.is_valid() and avatar_form.is_valid() and notification_form.is_valid():
            user_form.save()
            avatar_form.save()
            notification_form.save()
            messages.success(request, "Profile updated.")
            return redirect("accounts:profile")
    else:
        user_form = ProfileUserForm(instance=request.user)
        avatar_form = ProfileAvatarForm(instance=profile)
        notification_form = ProfileNotificationForm(instance=profile)

    return render(
        request,
        "accounts/profile.html",
        {
            "user_form": user_form,
            "avatar_form": avatar_form,
            "notification_form": notification_form,
            "profile": profile,
        },
    )


def _generate_username(first_name, last_name):
    """First name if free, else first name + first initial of last name,
    else fall back to appending a number."""
    base = slugify(first_name).replace("-", "") or "user"
    if not User.objects.filter(username__iexact=base).exists():
        return base

    last_initial = slugify(last_name)[:1] if last_name else ""
    candidate = f"{base}{last_initial}" if last_initial else base
    if candidate != base and not User.objects.filter(username__iexact=candidate).exists():
        return candidate

    suffix = 2
    while User.objects.filter(username__iexact=f"{candidate}{suffix}").exists():
        suffix += 1
    return f"{candidate}{suffix}"


def _send_account_created_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_path = reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})
    reset_url = request.build_absolute_uri(reset_path)
    message = render_to_string(
        "accounts/account_created_email.txt",
        {"user": user, "reset_url": reset_url},
    )
    send_mail(
        "Your Oakholm account has been created",
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=True,
    )


@login_required
@user_passes_test(lambda u: u.is_superuser)
def create_account_view(request):
    if request.method == "POST":
        form = CreateAccountForm(request.POST)
        if form.is_valid():
            person = form.cleaned_data["person"]
            email = form.cleaned_data["email"]
            add_approver = form.cleaned_data["is_approver"]

            username = _generate_username(person.first_name, person.last_name)
            new_user = User.objects.create_user(
                username=username,
                email=email,
                first_name=person.first_name,
                last_name=person.last_name,
                password=get_random_string(32),
            )

            person.user = new_user
            person.save()

            requesters_group, _ = Group.objects.get_or_create(name="Requesters")
            new_user.groups.add(requesters_group)
            if add_approver:
                approvers_group, _ = Group.objects.get_or_create(name="Approvers")
                new_user.groups.add(approvers_group)

            _send_account_created_email(request, new_user)

            messages.success(
                request,
                f"Account created for {person.full_name} (username: {username}). "
                f"A password setup email was sent to {email}.",
            )
            return redirect("accounts:create_account")
    else:
        form = CreateAccountForm()

    return render(request, "accounts/create_account.html", {"form": form})
