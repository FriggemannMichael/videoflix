# API endpoints

All endpoints are prefixed with `/api/`. Authentication uses HTTP-only JWT
cookies (`access_token` / `refresh_token`) set on login; authenticated
requests must be sent with credentials.

## Authentication

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| POST | `/register/` | – | Register a new (inactive) user; sends an activation email. |
| GET | `/activate/<uidb64>/<token>/` | – | Activate an account via the emailed link. |
| POST | `/login/` | – | Log in; sets the JWT auth cookies. |
| POST | `/logout/` | cookie | Log out; blacklists the refresh token and clears the cookies. |
| POST | `/token/refresh/` | cookie | Issue a new access token from the refresh cookie. |
| POST | `/password_reset/` | – | Request a password-reset email (identical response for known/unknown addresses). |
| POST | `/password_confirm/<uidb64>/<token>/` | – | Set a new password via the emailed link. |

## Videos and HLS

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| GET | `/video/` | ✓ | List completed videos, newest first. |
| GET | `/video/<movie_id>/<resolution>/index.m3u8` | ✓ | HLS playlist for a resolution (`application/vnd.apple.mpegurl`). |
| GET | `/video/<movie_id>/<resolution>/<segment>` | ✓ | HLS segment (`video/mp2t`). |

### Notes

- `resolution` is one of `480p`, `720p`, `1080p`; any other value returns 404.
- Segments are named `NNN.ts` (e.g. `000.ts`). The route has **no** trailing
  slash so `hls.js` loads segments directly without a redirect. The segment
  name is validated against `^[0-9]+\.ts$` to prevent path traversal.
- Playlist and segment requests return 404 for unknown videos, videos that are
  not yet `completed`, invalid resolutions, and missing files; unauthenticated
  requests return 401.
