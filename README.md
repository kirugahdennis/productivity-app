# Journal API

A Flask REST API for a personal journal-tracking app, built for the
Auth + User-Owned Resource summative lab. Implements **session-based
authentication** and full **CRUD** on a user-owned `JournalEntry`
resource, with pagination and strict per-user access. 

## Stack

- Flask 2.2.2 + Flask-RESTful (Resource-based routing)
- Flask-SQLAlchemy 3.0.3 + Flask-Migrate 4.0.0
- Flask-Bcrypt 1.0.1 (password hashing)
- Marshmallow 3.20.1 (request validation/serialization)
- Faker 15.3.2 (seeding)
- Flask-CORS (cross-origin cookies for a separately-hosted frontend)
- Pytest 7.2.0

## Project structure
journal-api/
├── Pipfile
├── pytest.ini
├── server/
│ ├── app.py # App factory + route registration
│ ├── config.py # Config (DB URI, secret key, cookie settings)
│ ├── extensions.py # db, migrate, bcrypt singletons
│ ├── helpers.py # @login_required decorator, current_user()
│ ├── schemas.py # Marshmallow validation schemas
│ ├── seed.py # Faker-based DB seeding
│ ├── models/
│ │ ├── user.py # User model (password hashing, validation)
│ │ └── journal_entry.py# JournalEntry model (the owned resource)
│ └── routes/
│ ├── auth.py # Signup, Login, Logout, CheckSession
│ └── journal_entries.py # CRUD + pagination + ownership checks
└── tests/
├── conftest.py
├── test_auth.py
└── test_journal_entries.py


### Access control

- Every entry route is wrapped in `@login_required`; no session, no
  access, `401`.
- Every single-entry route (`GET`/`PATCH`/`DELETE /journal_entries/<id>`)
  looks the entry up **scoped to the current user's id**. If the
  entry doesn't exist *or* belongs to someone else, the response is a
  **404**, not a 403 — this avoids leaking which entry ids exist for
  other accounts.
- The index route filters at the query level (`filter_by(user_id=...)`),
  so there's no way to page into another user's data via `page`/`per_page`.

## Seeding

`python -m server.seed` clears existing data and creates:
- A fixed demo account: `demo_user` / `password123`
- 4 additional random users (Faker), same password
- 8–15 Faker-generated journal entries per user, with random moods

## Testing

```bash
pytest
```

## Author
Denis Kiarie.
