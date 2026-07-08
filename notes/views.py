from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import NoteForm
from .models import AUTO_ARCHIVE_AFTER, Note, NoteImage


def _active_notes_queryset():
    cutoff = timezone.now() - AUTO_ARCHIVE_AFTER
    return Note.objects.filter(is_archived=False, created_at__gt=cutoff).select_related(
        "author"
    ).prefetch_related("images")


def _archived_notes_queryset():
    cutoff = timezone.now() - AUTO_ARCHIVE_AFTER
    return Note.objects.filter(Q(is_archived=True) | Q(created_at__lte=cutoff)).select_related(
        "author"
    ).prefetch_related("images")


@login_required
def notes_list_view(request):
    if request.method == "POST":
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.author = request.user
            note.save()
            for f in request.FILES.getlist("images"):
                NoteImage.objects.create(note=note, image=f, uploaded_by=request.user)
            messages.success(request, "Note added.")
            return redirect("notes:list")
    else:
        form = NoteForm()

    notes = _active_notes_queryset()
    return render(request, "notes/list.html", {"form": form, "notes": notes})


@login_required
def archived_notes_view(request):
    notes = _archived_notes_queryset()
    return render(request, "notes/archived_list.html", {"notes": notes})


@login_required
def note_edit_view(request, note_id):
    note = get_object_or_404(Note, pk=note_id, author=request.user)

    if request.method == "POST":
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            for f in request.FILES.getlist("images"):
                NoteImage.objects.create(note=note, image=f, uploaded_by=request.user)
            messages.success(request, "Note updated.")
            return redirect("notes:list")
    else:
        form = NoteForm(instance=note)

    return render(request, "notes/edit.html", {"form": form, "note": note})


@login_required
@require_POST
def note_delete(request, note_id):
    note = get_object_or_404(Note, pk=note_id, author=request.user)
    note.delete()
    messages.success(request, "Note deleted.")
    return redirect("notes:list")


@login_required
@require_POST
def note_archive(request, note_id):
    note = get_object_or_404(Note, pk=note_id)
    if not request.user.is_superuser:
        messages.error(request, "Only an admin can archive notes.")
        return redirect("notes:list")
    note.is_archived = True
    note.archived_at = timezone.now()
    note.save()
    messages.success(request, "Note archived.")
    return redirect("notes:list")


@login_required
@require_POST
def note_unarchive(request, note_id):
    note = get_object_or_404(Note, pk=note_id)
    if not request.user.is_superuser:
        messages.error(request, "Only an admin can unarchive notes.")
        return redirect("notes:archived")
    note.is_archived = False
    note.archived_at = None
    note.save()
    messages.success(request, "Note restored.")
    return redirect("notes:archived")
