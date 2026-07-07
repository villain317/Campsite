from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Checklist, ChecklistImage, ChecklistItem, ChecklistRun, ChecklistRunItem


def _get_or_create_active_run(user, checklist):
    """Get the user's in-progress run for this checklist, creating one if
    needed, and make sure it has a ChecklistRunItem for every item currently
    on the template (so items added later show up on runs already underway).
    """
    run, _ = ChecklistRun.objects.get_or_create(
        user=user, checklist=checklist, status=ChecklistRun.STATUS_IN_PROGRESS
    )
    existing_item_ids = set(run.run_items.values_list("item_id", flat=True))
    missing_items = checklist.items.exclude(id__in=existing_item_ids)
    ChecklistRunItem.objects.bulk_create(
        [ChecklistRunItem(run=run, item=item) for item in missing_items]
    )
    return run


@login_required
def checklist_run_view(request, checklist_id):
    checklist = get_object_or_404(Checklist, pk=checklist_id)
    run = _get_or_create_active_run(request.user, checklist)
    run_items = run.run_items.select_related("item").order_by("item__created_at", "item__id")
    images = run.images.all()

    context = {
        "checklist": checklist,
        "run": run,
        "run_items": run_items,
        "images": images,
    }
    return render(request, "checklists/run.html", context)


@login_required
@require_POST
def toggle_item(request, run_item_id):
    run_item = get_object_or_404(
        ChecklistRunItem, pk=run_item_id, run__user=request.user, run__status=ChecklistRun.STATUS_IN_PROGRESS
    )
    run_item.checked = not run_item.checked
    run_item.checked_at = timezone.now() if run_item.checked else None
    run_item.save()
    return JsonResponse({"checked": run_item.checked})


@login_required
@require_POST
def add_item(request, run_id):
    run = get_object_or_404(ChecklistRun, pk=run_id, user=request.user, status=ChecklistRun.STATUS_IN_PROGRESS)
    name = request.POST.get("name", "").strip()
    if name:
        item = ChecklistItem.objects.create(checklist=run.checklist, name=name)
        ChecklistRunItem.objects.create(run=run, item=item)
        messages.success(request, f"Added '{name}' to {run.checklist.name}.")
    else:
        messages.error(request, "Item name can't be blank.")
    return redirect("checklists:run", checklist_id=run.checklist_id)


@login_required
@require_POST
def upload_image(request, run_id):
    run = get_object_or_404(ChecklistRun, pk=run_id, user=request.user, status=ChecklistRun.STATUS_IN_PROGRESS)
    files = request.FILES.getlist("images")
    if not files:
        messages.error(request, "No image selected.")
    for f in files:
        ChecklistImage.objects.create(run=run, image=f, uploaded_by=request.user)
    if files:
        messages.success(request, "Photo(s) uploaded.")
    return redirect("checklists:run", checklist_id=run.checklist_id)


@login_required
@require_POST
def complete_run(request, run_id):
    run = get_object_or_404(ChecklistRun, pk=run_id, user=request.user, status=ChecklistRun.STATUS_IN_PROGRESS)
    run.status = ChecklistRun.STATUS_COMPLETED
    run.completed_at = timezone.now()
    run.save()
    messages.success(request, f"{run.checklist.name} completed!")
    return redirect("checklists:run", checklist_id=run.checklist_id)


@login_required
def completed_list_view(request):
    checked_items_qs = ChecklistRunItem.objects.filter(checked=True).select_related("item")
    runs = (
        ChecklistRun.objects.filter(status=ChecklistRun.STATUS_COMPLETED)
        .select_related("checklist", "user")
        .prefetch_related(
            Prefetch("run_items", queryset=checked_items_qs, to_attr="checked_items"),
            "images",
        )
        .order_by("-completed_at")
    )
    return render(request, "checklists/completed_list.html", {"runs": runs})
