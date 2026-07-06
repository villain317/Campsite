from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Family

APPROVERS_GROUP_NAME = "Approvers"


@receiver(post_save, sender=Family)
def add_head_account_to_approvers_group(sender, instance, **kwargs):
    """Whenever a family is created/updated, make sure the head account
    is in the Approvers group so they can access the approval page."""
    group, _ = Group.objects.get_or_create(name=APPROVERS_GROUP_NAME)
    instance.head_account.groups.add(group)
