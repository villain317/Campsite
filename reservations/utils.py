def is_approver(user):
    """Approvers are family heads (Approvers group) or superusers."""
    if not user.is_authenticated:
        return False
    return user.is_superuser or user.groups.filter(name="Approvers").exists()


def build_people_picker_context(form):
    """Build the family/household/people structure for the request form template.

    Returns a dict with:
      - family_data: list of dicts, one per Family, each with:
          - family: the Family instance
          - households: list of Household instances (with .members prefetched)
          - ungrouped: list of Person instances not in a household
      - selected_ids: set of currently-selected person ids, accounting for
        bound (re-rendered after a validation error), instance (editing), and
        fresh (initial default) form states.
    """
    from .models import Family

    if form.is_bound:
        raw_ids = form.data.getlist("people")
        selected_ids = {int(v) for v in raw_ids if str(v).isdigit()}
    elif form.instance.pk:
        selected_ids = set(form.instance.people.values_list("pk", flat=True))
    else:
        selected_ids = set(form.fields["people"].initial or [])

    family_data = []
    families = Family.objects.prefetch_related("households__members", "members").order_by("name")
    for family in families:
        households = list(family.households.all())
        household_member_ids = {p.pk for h in households for p in h.members.all()}
        ungrouped = [p for p in family.members.all() if p.pk not in household_member_ids]
        family_data.append({
            "family": family,
            "households": households,
            "ungrouped": ungrouped,
        })

    return {"family_data": family_data, "selected_ids": selected_ids}
