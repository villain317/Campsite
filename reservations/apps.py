from django.apps import AppConfig


class ReservationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "reservations"
    verbose_name = "Oakholm Reservations"

    def ready(self):
        # Register signal handlers (e.g. auto-adding family heads to the
        # Approvers group).
        from . import signals  # noqa: F401
