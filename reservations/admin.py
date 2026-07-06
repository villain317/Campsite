from django import forms
from django.contrib import admin
from django.utils.html import format_html

from .models import Family, Person, ReservationRequest


class FamilyAdminForm(forms.ModelForm):
    class Meta:
        model = Family
        fields = "__all__"
        widgets = {
            "color": forms.TextInput(
                attrs={"type": "color", "style": "width: 5rem; height: 2.5rem; padding: 2px;"}
            ),
        }


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    form = FamilyAdminForm
    list_display = ("name", "color_swatch", "color", "head_account")
    search_fields = ("name",)

    @admin.display(description="")
    def color_swatch(self, obj):
        return format_html(
            '<span style="display:inline-block;width:1.2rem;height:1.2rem;'
            'border-radius:3px;border:1px solid #ccc;background-color:{};"></span>',
            obj.color,
        )


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "family", "user")
    list_filter = ("family",)
    search_fields = ("first_name", "last_name")


@admin.register(ReservationRequest)
class ReservationRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "requested_by",
        "start_date",
        "end_date",
        "estimated_occupants",
        "status",
        "requested_at",
    )
    list_filter = ("status",)
    filter_horizontal = ("people",)
    autocomplete_fields = ("requested_by", "decided_by")
    search_fields = ("requested_by__username", "requested_by__email")
