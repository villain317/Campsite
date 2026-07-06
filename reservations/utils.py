def is_approver(user):
    """Approvers are family heads (Approvers group) or superusers."""
    if not user.is_authenticated:
        return False
    return user.is_superuser or user.groups.filter(name="Approvers").exists()
