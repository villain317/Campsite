"""
URL configuration for campsite project.
"""
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path, re_path
from django.views.static import serve as serve_static

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("checklists/", include("checklists.urls")),
    path("", include("reservations.urls")),
]

# Serve /media/ (the banner image, checklist photos, etc.) through Django
# directly, in both dev and production. Django's usual
# django.conf.urls.static.static() helper silently no-ops when DEBUG=False,
# which is why this uses django.views.static serve directly instead. For a
# low-traffic site like this, having Django serve media is perfectly fine; if
# traffic/upload volume ever grows, this is a good candidate to move to
# Caddy's file_server or object storage instead.
urlpatterns += [
    re_path(r"^media/(?P<path>.*)$", serve_static, {"document_root": settings.MEDIA_ROOT}),
]
