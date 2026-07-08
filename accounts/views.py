from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ProfileAvatarForm, ProfileUserForm
from .models import Profile


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        user_form = ProfileUserForm(request.POST, instance=request.user)
        avatar_form = ProfileAvatarForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and avatar_form.is_valid():
            user_form.save()
            avatar_form.save()
            messages.success(request, "Profile updated.")
            return redirect("accounts:profile")
    else:
        user_form = ProfileUserForm(instance=request.user)
        avatar_form = ProfileAvatarForm(instance=profile)

    return render(
        request,
        "accounts/profile.html",
        {"user_form": user_form, "avatar_form": avatar_form, "profile": profile},
    )
