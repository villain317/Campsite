# Oakholm Reservations

Django app for scheduling and approving stays at Oakholm, the family lake house.

## Run it

```bash
cp .env.example .env   # edit values, especially POSTGRES_PASSWORD and DJANGO_SECRET_KEY
docker compose up --build
```

The site is at http://localhost:8000/. Migrations, `collectstatic`, and group
seeding run automatically on container start.

Create an admin user:

```bash
docker compose exec web python manage.py createsuperuser
```

## Setting up families and people

Everything is managed through the Django admin (`/admin/`):

1. Create a `User` for each person who needs an account (the 3 heads of
   household, plus any kids/grandkids who should be able to log in).
2. Create a `Family` for each of the 3 branches: name, calendar color (hex),
   and the head's `User` account. The head is automatically added to the
   **Approvers** group and can access the approve-requests page.
3. Create a `Person` for every family member (first/last name, family). Tie a
   `Person` to a `User` if they should be able to log in and submit requests
   under their own name — this is optional.

## How it works

- **Calendar** (`/`) — month view, approved stays shown in each family's
  color, pending requests shown in gray. Anyone logged in can view it.
- **New Request** (`/request/new/`) — pick a date range, attendees (defaults
  to the requester's own family), and estimated occupant count. Submitting
  emails the family head.
- **Approve Requests** (`/approve/`) — visible only to Approvers (family
  heads/superusers). Shows pending requests as cards with an overlap warning
  and Approve/Deny buttons.

## Email

By default (no `EMAIL_HOST` set) emails are printed to the `web` container's
logs (`docker compose logs -f web`). Set `EMAIL_HOST`/`EMAIL_HOST_USER`/
`EMAIL_HOST_PASSWORD` in `.env` to send real email via SMTP.
