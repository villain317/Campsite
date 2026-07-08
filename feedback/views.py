from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render

from .forms import FeedbackForm
from .models import FeedbackItem


@login_required
def feedback_create_view(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.author = request.user
            feedback.save()
            messages.success(request, "Thanks for the feedback!")
            return redirect("feedback:create")
    else:
        form = FeedbackForm()
    return render(request, "feedback/create.html", {"form": form})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def feedback_list_view(request):
    items = FeedbackItem.objects.select_related("author").all()
    return render(request, "feedback/list.html", {"items": items})
