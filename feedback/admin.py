from django.contrib import admin

from .models import FeedbackItem


@admin.register(FeedbackItem)
class FeedbackItemAdmin(admin.ModelAdmin):
    list_display = ("author", "created_at")
    list_filter = ("created_at",)
    search_fields = ("message", "author__username", "author__first_name", "author__last_name")
    readonly_fields = ("author", "message", "created_at")
