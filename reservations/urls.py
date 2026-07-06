from django.urls import path

from . import views

app_name = "reservations"

urlpatterns = [
    path("", views.calendar_view, name="calendar"),
    path("request/new/", views.request_create, name="request_create"),
    path("approve/", views.approve_list, name="approve_list"),
    path("approve/<int:pk>/<str:action>/", views.approve_action, name="approve_action"),
]
