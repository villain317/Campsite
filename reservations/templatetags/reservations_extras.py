from django import template

from reservations.utils import is_approver as _is_approver

register = template.Library()


@register.filter(name="is_approver")
def is_approver(user):
    return _is_approver(user)
