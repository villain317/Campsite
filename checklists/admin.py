from django.contrib import admin

from .models import Checklist, ChecklistImage, ChecklistItem, ChecklistRun, ChecklistRunItem


class ChecklistItemInline(admin.TabularInline):
    model = ChecklistItem
    extra = 1


@admin.register(Checklist)
class ChecklistAdmin(admin.ModelAdmin):
    list_display = ("name",)
    inlines = [ChecklistItemInline]


@admin.register(ChecklistItem)
class ChecklistItemAdmin(admin.ModelAdmin):
    list_display = ("name", "checklist", "is_active", "created_at")
    list_filter = ("checklist", "is_active")


class ChecklistRunItemInline(admin.TabularInline):
    model = ChecklistRunItem
    extra = 0
    readonly_fields = ("item", "checked", "checked_at")
    can_delete = False


class ChecklistImageInline(admin.TabularInline):
    model = ChecklistImage
    extra = 0
    readonly_fields = ("image", "uploaded_by", "uploaded_at")
    can_delete = False


@admin.register(ChecklistRun)
class ChecklistRunAdmin(admin.ModelAdmin):
    list_display = ("checklist", "user", "status", "started_at", "completed_at")
    list_filter = ("checklist", "status")
    inlines = [ChecklistRunItemInline, ChecklistImageInline]
