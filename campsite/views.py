from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def guide_view(request):
    """A plain-language guide to what the site can do, for end users."""
    return render(request, "guide.html")
