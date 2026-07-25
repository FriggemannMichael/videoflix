# Videoflix

Backend for the Videoflix streaming platform: a Django REST Framework API that
handles user accounts, serves a video dashboard, and delivers adaptive HLS
video streams. Uploaded videos are transcoded to multiple resolutions and
thumbnailed in the background, and the resulting playlists and segments are
served only to authenticated users.

This repository contains the **backend only**. The frontend is provided
separately by the Developer Akademie and talks to this API over REST.

## Features

- Email/password registration with an activation email; accounts are inactive
  until the emailed link is confirmed.
- Cookie-based JWT authentication (login, logout with refresh-token
  blacklisting, token refresh).
- Password reset by email with a secure, single-use confirmation link.
- Video dashboard endpoint (completed videos only, newest first) with a Redis
  cache layer.
- Background processing with Django-RQ: thumbnail extraction and HLS
  transcoding to 480p, 720p, and 1080p, both triggered automatically when a
  video is created.
- Protected HLS delivery of playlists (`.m3u8`) and segments (`.ts`), guarded
  against path traversal.

## Tech stack

- **Python** 3.12, **Django** 5.2, **Django REST Framework**
- **PostgreSQL** (database), **Redis** (cache + task queue)
- **Django-RQ** (background worker), **FFmpeg** (thumbnails + HLS)
- **djangorestframework-simplejwt** (JWT auth via HTTP-only cookies)
- **Gunicorn** + **WhiteNoise** (serving), **Docker Compose** (orchestration)
- **pytest** + coverage, **Ruff** (lint + format)

## Architecture

| App / module | Responsibility |
| --- | --- |
| `accounts` | Custom user model (email as username), registration, activation, login/logout, token refresh, password reset, cookie helpers, emails. |
| `videos` | Video model, list endpoint + serializer, Redis caching, RQ tasks (`generate_thumbnail`, `convert_to_hls`), HLS path layout (`hls.py`), playlist and segment delivery. |
| `core` | Project settings, URL routing, WSGI entry point. |
| `tests` | pytest suite and the Postman/Newman smoke-test collection. |

Creating a `Video` fires `post_save` signals that enqueue the thumbnail and
HLS-conversion tasks onto the `default` RQ queue. A worker (started by the
container entrypoint) runs FFmpeg and writes the HLS output to
`media/videos/hls/<video_id>/<resolution>/`, containing `index.m3u8` and
`000.ts`, `001.ts`, … segments. The video's `processing_status` moves from
`pending` → `processing` → `completed` (or `failed`), and only `completed`
videos appear on the dashboard and can be streamed.

## Getting started (Docker)

Docker is the recommended way to run the project; the image already includes
FFmpeg and the Postgres client.

```bash
git clone <repository-url>
cd videoflix
cp .env.template .env      # then edit the placeholder values (see below)
docker compose up --build
```

The API is then available at `http://127.0.0.1:8000/`. On startup the
entrypoint waits for PostgreSQL, runs migrations, collects static files,
creates the superuser from the `DJANGO_SUPERUSER_*` variables, starts an RQ
worker, and launches Gunicorn.

- **API base:** `http://127.0.0.1:8000/api/`
- **Django admin:** `http://127.0.0.1:8000/admin/` (default `admin` /
  `adminpassword` from `.env.template` — change these)

> Do not modify the provided Docker files (`docker-compose.yml`,
> `backend.Dockerfile`, `backend.entrypoint.sh`); they are part of the
> supplied setup.

### Adding a video

There is no public upload endpoint. Add videos through the Django admin
(`/admin/videos/video/add/`) by uploading an `original_file`. Saving the video
automatically enqueues thumbnail generation and HLS conversion; once the
worker finishes, the video's status becomes `completed` and it appears on the
dashboard.

## Environment variables

Copy `.env.template` to `.env` and adjust the values. `.env` is git-ignored.

| Variable | Purpose |
| --- | --- |
| `DJANGO_SUPERUSER_USERNAME` / `_PASSWORD` / `_EMAIL` | Superuser created on first startup. |
| `SECRET_KEY` | Django secret key. |
| `DEBUG` | `True` for development (also enables Django serving of `/media/`). |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts. |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated trusted origins. |
| `FRONTEND_URL` | Frontend origin; used for CORS and email links. |
| `DB_NAME` / `DB_USER` / `DB_PASSWORD` / `DB_HOST` / `DB_PORT` | PostgreSQL connection. |
| `REDIS_HOST` / `REDIS_PORT` / `REDIS_DB` / `REDIS_LOCATION` | Redis (queue + cache). |
| `EMAIL_HOST` / `EMAIL_PORT` / `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` / `EMAIL_USE_TLS` / `EMAIL_USE_SSL` / `DEFAULT_FROM_EMAIL` | SMTP configuration. |

Optional variables (sensible defaults if unset):

| Variable | Default | Purpose |
| --- | --- | --- |
| `EMAIL_BACKEND` | SMTP backend | Set to `django.core.mail.backends.console.EmailBackend` to print emails to the console during local development. |
| `ACCESS_TOKEN_LIFETIME_MINUTES` | `60` | JWT access-token lifetime. |
| `FFMPEG_PATH` | `ffmpeg` | Path to the FFmpeg binary. |

## Email setup

Registration and password reset send emails (HTML + plain text). For local
development set `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`
to print messages to the console instead of sending them. For real delivery,
configure the `EMAIL_*` SMTP variables. Activation and reset links point at
`FRONTEND_URL`, which handles the request and calls back into the API.

## HLS streaming

Videos are transcoded to `480p`, `720p`, and `1080p`. Clients (e.g. `hls.js`)
first load the playlist and then request the individual segments it lists:

```
GET /api/video/<movie_id>/<resolution>/index.m3u8   → application/vnd.apple.mpegurl
GET /api/video/<movie_id>/<resolution>/<segment>     → video/mp2t
```

Both endpoints require authentication, validate the resolution against a
whitelist, and reject anything but a numeric `NNN.ts` segment name to prevent
path traversal. Segment URLs intentionally have **no** trailing slash so
`hls.js` loads them directly without a redirect.

## Frontend integration

The frontend is a separate static app and communicates with this API over
REST. Authentication uses HTTP-only cookies (`access_token` /
`refresh_token`), so requests must be sent with credentials and the frontend
must be served from an origin listed in `CORS_ALLOWED_ORIGINS` (derived from
`FRONTEND_URL`; `CORS_ALLOW_CREDENTIALS` is enabled).

> Because the auth cookies are `SameSite=Lax`, open the frontend on the **same
> host** as the API (e.g. both on `127.0.0.1`, not `localhost` for one and
> `127.0.0.1` for the other), otherwise the cookies are treated as cross-site
> and are not sent.

## API endpoints

All endpoints are prefixed with `/api/`.

| Method | Path | Description |
| --- | --- | --- |
| POST | `/register/` | Register a new (inactive) user; sends an activation email. |
| GET | `/activate/<uidb64>/<token>/` | Activate an account via the emailed link. |
| POST | `/login/` | Log in; sets the JWT auth cookies. |
| POST | `/logout/` | Log out; blacklists the refresh token and clears cookies. |
| POST | `/token/refresh/` | Issue a new access token from the refresh cookie. |
| POST | `/password_reset/` | Request a password-reset email (identical response for known/unknown addresses). |
| POST | `/password_confirm/<uidb64>/<token>/` | Set a new password via the emailed link. |
| GET | `/video/` | List completed videos (authenticated), newest first. |
| GET | `/video/<movie_id>/<resolution>/index.m3u8` | HLS playlist for a resolution (authenticated). |
| GET | `/video/<movie_id>/<resolution>/<segment>` | HLS segment (authenticated). |

## Local development with uv

The project uses [uv](https://docs.astral.sh/uv/) for dependency management.
Running the full stack still needs PostgreSQL and Redis (easiest via
`docker compose up db redis`), plus FFmpeg on your `PATH` for the tasks.

```bash
uv sync                     # install dependencies into .venv
uv run python manage.py migrate
uv run python manage.py runserver
```

## Tests and code quality

Run inside the container (`docker compose exec web ...`) or via `uv run`:

```bash
pytest                              # test suite with branch coverage (fails under 95%)
ruff check .                        # lint
ruff format --check .              # formatting
python manage.py check             # Django system checks
python tests/scripts/check_size_limits.py   # max 14 LOC/function, 400 LOC/file
```

The Postman collection under `tests/postman/` is run as an API smoke test with
Newman:

```bash
npx newman run tests/postman/videoflix-api.postman_collection.json \
  --env-var baseUrl=http://127.0.0.1:8000
```

CI (`.github/workflows/`) runs the same lint, format, checks, tests, size
limits, Newman smoke tests, and a full Docker-Compose boot on every push.

## Known limitations

- Django serves `/media/` only when `DEBUG=True`; a production deployment needs
  a reverse proxy (e.g. nginx) to serve media and static files.
- Videos are added through the Django admin; there is no public upload API.
- The Postman smoke tests cover the auth flows and the video list; HLS playlist
  and segment delivery are covered by the pytest suite (the CI smoke-test
  database has no transcoded media to serve).
