"""
URL configuration for campsite project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", include("reservations.urls")),
]

if settings.DEBUG:
    # Serve /media/ locally in dev. In production, media should be served by
    # a real web server, whitenoise-style storage, or object storage (S3 etc.)
    # rather than through Django.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
