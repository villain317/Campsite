from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create the default auth groups (Approvers, Requesters) if they don't exist."

    def handle(self, *args, **options):
        for name in ("Approvers", "Requesters"):
            _, created = Group.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created group '{name}'"))
            else:
                self.stdout.write(f"Group '{name}' already exists")
