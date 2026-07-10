from django.urls import path

from . import views

app_name = "notes"

urlpatterns = [
    path("", views.notes_list_view, name="list"),
    path("archived/", views.archived_notes_view, name="archived"),
    path("<int:note_id>/edit/", views.note_edit_view, name="edit"),
    path("<int:note_id>/delete/", views.note_delete, name="delete"),
    path("<int:note_id>/archive/", views.note_archive, name="archive"),
    path("<int:note_id>/unarchive/", views.note_unarchive, name="unarchive"),
    path("<int:note_id>/claim/", views.note_claim, name="claim"),
    path("<int:note_id>/unclaim/", views.note_unclaim, name="unclaim"),
]
