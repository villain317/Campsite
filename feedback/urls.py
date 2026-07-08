from django.urls import path

from . import views

app_name = "feedback"

urlpatterns = [
    path("", views.feedback_create_view, name="create"),
    path("all/", views.feedback_list_view, name="list"),
]
