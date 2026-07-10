from django.urls import path

from . import views

app_name = "checklists"

urlpatterns = [
    path("create/", views.create_checklist, name="create"),
    path("completed/", views.completed_list_view, name="completed_list"),
    path("<int:checklist_id>/", views.checklist_run_view, name="run"),
    path("<int:run_id>/add-item/", views.add_item, name="add_item"),
    path("<int:run_id>/upload-image/", views.upload_image, name="upload_image"),
    path("<int:run_id>/update-notes/", views.update_notes, name="update_notes"),
    path("<int:run_id>/complete/", views.complete_run, name="complete_run"),
    path("item/<int:run_item_id>/toggle/", views.toggle_item, name="toggle_item"),
    path("item/<int:item_id>/edit/", views.edit_item, name="edit_item"),
    path("item/<int:item_id>/delete/", views.delete_item, name="delete_item"),
    path("<int:run_id>/delete/", views.delete_run, name="delete_run"),
]
