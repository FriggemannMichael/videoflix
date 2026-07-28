# Videoflix Backend

A Django REST Framework backend for a video streaming platform: user accounts,
a video dashboard, and adaptive HLS delivery. Uploaded videos are transcoded to
multiple resolutions and thumbnailed in the background, and the resulting
playlists and segments are served only to authenticated users. This repository
contains the backend only; the frontend is provided separately.

## Setup

The recommended way to run Videoflix is Docker Compose. The image already
bundles FFmpeg and the Postgres client, and the entrypoint waits for the
database, runs migrations, collects static files, creates the superuser from
the `DJANGO_SUPERUSER_*` variables, and starts an RQ worker.

```bash
git clone <repository-url>
cd videoflix
cp .env.template .env      # adjust the placeholder values
docker compose up --build
```

- API base: `http://127.0.0.1:8000/api/`
- Django admin: `http://127.0.0.1:8000/admin/`

### Environment variables

`cp .env.template .env` brings in every variable the project reads. These are
the ones that decide whether a fresh clone actually works — the rest can stay
on their template values.

```bash
SECRET_KEY=...                                # Django signing key
DEBUG=True                                    # also serves /media/ locally
ALLOWED_HOSTS=localhost,127.0.0.1             # hosts the backend answers for
CSRF_TRUSTED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
CORS_ALLOWED_ORIGINS=http://127.0.0.1:5500    # origin the frontend is served from
FRONTEND_EMAIL_LINK_URL=http://127.0.0.1:5500 # host the mail links point to

DB_NAME=...                                   # the Postgres container creates the
DB_USER=...                                   # database from these three, and
DB_PASSWORD=...                               # Django logs in with them
DB_HOST=db                                    # compose service names
DB_PORT=5432

REDIS_LOCATION=redis://redis:6379/1           # cache
REDIS_HOST=redis                              # RQ queue
REDIS_PORT=6379
REDIS_DB=0

DJANGO_SUPERUSER_USERNAME=admin               # the entrypoint creates this
DJANGO_SUPERUSER_PASSWORD=adminpassword       # account on first start
DJANGO_SUPERUSER_EMAIL=admin@example.com

EMAIL_BACKEND=...smtp.EmailBackend            # console backend also possible,
EMAIL_HOST=smtp.example.com                   # replace with real credentials,
EMAIL_HOST_USER=...                           # see the note below
EMAIL_HOST_PASSWORD=...
DEFAULT_FROM_EMAIL=...
```

The last two of the first group look alike and usually hold the same value, but
they answer different questions: `CORS_ALLOWED_ORIGINS` decides which origin a
browser may call the API from, while `FRONTEND_EMAIL_LINK_URL` only builds the
links inside the activation and password reset mails.

**The email settings are not optional.** The template ships the SMTP backend, so
left on the placeholder credentials, registration cannot reach
`smtp.example.com` and the request answers 500. No half-created account is left
behind — creating the user and sending the mail share one transaction — but
registering is impossible. Either enter real SMTP credentials, or print the
mails to the container log instead:

```bash
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

> **Serve the frontend from `127.0.0.1:5500`, not from `localhost:5500`.**
>
> The frontend is a separate project — see
> [project.Videoflix](https://github.com/Developer-Akademie-Backendkurs/project.Videoflix)
> for how to start it.
>
> It calls the API at `http://127.0.0.1:8000/api/`, and the auth cookies are
> `SameSite=Lax`. Served from `localhost:5500`, the browser treats every API
> call as cross-site: the origin is not in `CORS_ALLOWED_ORIGINS`, so the
> request is rejected, and even if the origin were allowed the login cookie
> would still be dropped. On `127.0.0.1:5500` both sides share a host and
> everything works — which is why it is the default of both
> `CORS_ALLOWED_ORIGINS` and `FRONTEND_EMAIL_LINK_URL`.

### Local development (without Docker)

The project uses [uv](https://docs.astral.sh/uv/). Running the app still needs
PostgreSQL, Redis, and FFmpeg available (the databases are easiest via
`docker compose up db redis`).

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

## Live demo

There is no public deployment — Videoflix is submitted as a backend-only
GitHub repository. To experience it end to end, run the stack above and serve
the [frontend](https://github.com/Developer-Akademie-Backendkurs/project.Videoflix)
against it on `http://127.0.0.1:5500`, for the reason described in the setup
section.

## Features

- **Authentication** — registration with an email activation link, cookie-based
  JWT login, token refresh, and logout with refresh-token blacklisting.
- **Password reset** — request and confirm a reset by email, without revealing
  whether an address exists.
- **Video dashboard** — lists completed videos (newest first) with title,
  category, and thumbnail, served through a Redis cache.
- **Background processing** — Django-RQ tasks transcode each upload to HLS
  (480p/720p/1080p) and extract a thumbnail with FFmpeg.
- **Protected HLS delivery** — authenticated playlist (`.m3u8`) and segment
  (`.ts`) endpoints, guarded against path traversal.

The full endpoint reference lives in [docs/endpoints.md](docs/endpoints.md).

## Tech stack

- **Python** 3.12, **Django** 5.2, **Django REST Framework**
- **djangorestframework-simplejwt** for JWT auth via HTTP-only cookies
- **PostgreSQL** (database), **Redis** (cache + task queue via Django-RQ)
- **FFmpeg** for thumbnails and HLS transcoding
- **Gunicorn** + **WhiteNoise**, **Docker Compose**, **pytest** + coverage, **Ruff**

## User types and authentication

- **Registered viewer** — signs up with email and password, activates the
  account via the emailed link, then browses and streams videos.
- **Staff / superuser** — manages the video catalogue through the Django admin;
  uploading a video automatically enqueues thumbnail and HLS conversion. There
  is no public upload endpoint.

Authentication uses HTTP-only cookies set on login:

```
access_token   (short-lived, sent automatically with each request)
refresh_token  (used by POST /api/token/refresh/)
```

Create an admin to manage videos (or use the superuser created from `.env`):

```bash
docker compose exec web python manage.py createsuperuser
```

## Project structure

- `core/` — Django project configuration, URL routing, WSGI entry point
- `accounts/` — custom user model, registration, activation, login/logout,
  token refresh, password reset, cookie helpers, emails
- `videos/` — video model, list endpoint, Redis caching, RQ tasks
  (`generate_thumbnail`, `convert_to_hls`), HLS layout, playlist/segment delivery
- `tests/` — pytest suite plus the Postman/Newman smoke-test collection
- `docs/` — endpoint reference and the delivery checklist

## Running checks

Run inside the container (`docker compose exec web ...`) or via `uv run`.

Django's built-in checks:

```bash
python manage.py check
```

Lint and formatting:

```bash
ruff check .
ruff format --check .
```

Tests with branch coverage (the threshold is 95%, configured in `pyproject.toml`):

```bash
pytest
```

Function and file size limits (max 14 LOC per function, 400 LOC per file):

```bash
python tests/scripts/check_size_limits.py
```

## Delivery checklist

The project's definition of done is tracked in
[docs/Videoflix Checkliste.md](docs/Videoflix%20Checkliste.md). Key backend
requirements:

- Backend and frontend are separated and communicate over a DRF REST API.
- Heavy work runs in the background via Django-RQ; Redis provides the cache.
- PostgreSQL is used instead of SQLite.
- The project starts fully via Docker Compose.
- Tests pass with 100% coverage, and Ruff, size limits, and the Postman smoke
  tests are green in CI.

## Repository hygiene

The following are intentionally excluded from version control (see `.gitignore`):

- `.env` — local secrets and configuration
- `media/` and `/static/` — generated uploads, HLS output, and collected static files
- `db.sqlite3` — only relevant for non-Docker experiments
- `__pycache__/`, `*.pyc`, `*.egg-info/` — Python build artifacts
- `.venv/`, `.coverage`, `.pytest_cache/` — local environment and test caches
- `.idea/`, `.vscode/` — IDE settings
