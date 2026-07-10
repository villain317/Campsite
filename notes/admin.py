from django.contrib import admin

from .models import Note, NoteImage


class NoteImageInline(admin.TabularInline):
    model = NoteImage
    extra = 0
    readonly_fields = ("image", "uploaded_by", "uploaded_at")


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("author", "category", "created_at", "is_archived", "is_claimed", "is_effectively_archived")
    list_filter = ("category", "is_archived", "is_claimed")
    search_fields = ("body", "author__username")
    inlines = [NoteImageInline]
