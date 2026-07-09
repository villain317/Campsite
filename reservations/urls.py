from django.urls import path

from . import views

app_name = "reservations"

urlpatterns = [
    path("", views.calendar_view, name="calendar"),
    path("request/new/", views.request_create, name="request_create"),
    path("requests/mine/", views.my_requests_view, name="my_requests"),
    path("request/<int:pk>/edit/", views.request_edit_view, name="request_edit"),
    path("approve/", views.approve_list, name="approve_list"),
    path("approve/<int:pk>/<str:action>/", views.approve_action, name="approve_action"),
]
