import calendar
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .emails import notify_family_head_of_request
from .forms import ReservationRequestForm
from .models import ReservationRequest
from .utils import is_approver

MONTH_NAMES = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def _add_months(year, month, delta):
    """Return (year, month) shifted by delta months."""
    total = (year * 12 + (month - 1)) + delta
    return total // 12, total % 12 + 1


@login_required
def calendar_view(request):
    today = date.today()
    try:
        center_year = int(request.GET.get("year", today.year))
        center_month = int(request.GET.get("month", today.month))
        date(center_year, center_month, 1)  # validate
    except (ValueError, TypeError):
        center_year, center_month = today.year, today.month

    cal = calendar.Calendar(firstweekday=6)  # weeks start on Sunday

    # Show 3 months at a time: the requested month, flanked by the month
    # before and the month after, so the requested month lands in the middle.
    months_to_show = [_add_months(center_year, center_month, offset) for offset in (-1, 0, 1)]
    month_grids = [(y, m, list(cal.itermonthdates(y, m))) for y, m in months_to_show]

    grid_start = month_grids[0][2][0]
    grid_end = month_grids[-1][2][-1]
    relevant_requests = list(
        ReservationRequest.objects.filter(
            status__in=[ReservationRequest.STATUS_APPROVED, ReservationRequest.STATUS_PENDING],
            start_date__lte=grid_end,
            end_date__gte=grid_start,
        ).prefetch_related("people", "people__family", "requested_by")
    )

    # Precompute display info for each request once.
    request_info = []
    for r in relevant_requests:
        family = r.family
        attendee_names = ", ".join(p.full_name for p in r.people.all())
        request_info.append(
            {
                "request": r,
                "family": family,
                "color": family.color if (family and r.status == ReservationRequest.STATUS_APPROVED) else "#adb5bd",
                "attendee_names": attendee_names,
            }
        )

    months = []
    for y, m, month_dates in month_grids:
        weeks = []
        week = []
        for d in month_dates:
            day_events = [
                info for info in request_info if info["request"].start_date <= d <= info["request"].end_date
            ]
            week.append({
                "date": d,
                "in_month": d.month == m,
                "is_today": d == today,
                "events": day_events,
            })
            if len(week) == 7:
                weeks.append(week)
                week = []
        months.append({
            "year": y,
            "month": m,
            "month_name": MONTH_NAMES[m],
            "weeks": weeks,
            "is_center": (y, m) == (center_year, center_month),
        })

    prev_year, prev_month = _add_months(center_year, center_month, -1)
    next_year, next_month = _add_months(center_year, center_month, 1)

    families = {info["family"] for info in request_info if info["family"]}

    context = {
        "months": months,
        "year": center_year,
        "month": center_month,
        "prev_month": prev_month,
        "prev_year": prev_year,
        "next_month": next_month,
        "next_year": next_year,
        "today": today,
        "families": sorted(families, key=lambda f: f.name),
    }
    return render(request, "reservations/calendar.html", context)


@login_required
def request_create(request):
    if request.method == "POST":
        form = ReservationRequestForm(request.POST, user=request.user)
        if form.is_valid():
            reservation_request = form.save(commit=False)
            reservation_request.requested_by = request.user
            reservation_request.save()
            form.save_m2m()
            notify_family_head_of_request(reservation_request)
            messages.success(request, "Your request has been submitted.")
            return redirect("reservations:calendar")
    else:
        form = ReservationRequestForm(user=request.user)

    return render(request, "reservations/request_form.html", {"form": form})


@login_required
@user_passes_test(is_approver)
def approve_list(request):
    pending_requests = (
        ReservationRequest.objects.filter(status=ReservationRequest.STATUS_PENDING)
        .select_related("requested_by")
        .prefetch_related("people", "people__family")
        .order_by("start_date")
    )

    cards = []
    for r in pending_requests:
        cards.append({
            "request": r,
            "family": r.family,
            "overlaps": r.overlapping_requests(),
        })

    return render(request, "reservations/approve_list.html", {"cards": cards})


@login_required
@user_passes_test(is_approver)
@require_POST
def approve_action(request, pk, action):
    reservation_request = get_object_or_404(ReservationRequest, pk=pk)

    if action == "approve":
        reservation_request.status = ReservationRequest.STATUS_APPROVED
        messages.success(request, "Request approved.")
    elif action == "deny":
        reservation_request.status = ReservationRequest.STATUS_DENIED
        messages.success(request, "Request denied.")
    else:
        messages.error(request, "Unknown action.")
        return redirect("reservations:approve_list")

    reservation_request.decided_by = request.user
    reservation_request.decided_at = timezone.now()
    reservation_request.save()

    return redirect("reservations:approve_list")
