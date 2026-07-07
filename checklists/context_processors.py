from .models import Checklist


def nav_checklists(request):
    """Make the list of checklists available to every template, for the nav
    dropdown. Only bother querying for logged-in users."""
    if not request.user.is_authenticated:
        return {}
    return {"nav_checklists": Checklist.objects.all()}
