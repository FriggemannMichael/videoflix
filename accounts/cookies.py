"""Reading and writing the JWT auth cookies.

The API never returns tokens for the frontend to store. Both the access and
the refresh token travel in HTTP-only cookies instead, so no script can read
them. Their ``SameSite`` and ``Secure`` flags come from the settings because
the frontend runs on a different host than the API.
"""

from django.conf import settings

ACCESS_TOKEN_COOKIE_NAME = 'access_token'
REFRESH_TOKEN_COOKIE_NAME = 'refresh_token'
AUTH_COOKIE_HTTP_ONLY = True


def set_auth_cookies(response, access_token, refresh_token):
    """Attach both the access and refresh token cookies to the response."""
    set_access_token_cookie(response, access_token)
    _set_cookie(response, REFRESH_TOKEN_COOKIE_NAME, refresh_token)


def set_access_token_cookie(response, access_token):
    """Store a (refreshed) access token as an HTTP-only cookie on the response."""
    _set_cookie(response, ACCESS_TOKEN_COOKIE_NAME, access_token)


def delete_auth_cookies(response):
    """Remove both the access and refresh token cookies from the response."""
    samesite = settings.AUTH_COOKIE_SAMESITE
    response.delete_cookie(ACCESS_TOKEN_COOKIE_NAME, samesite=samesite)
    response.delete_cookie(REFRESH_TOKEN_COOKIE_NAME, samesite=samesite)


def _set_cookie(response, name, value):
    """Write a single HTTP-only auth cookie with the shared security flags."""
    response.set_cookie(
        name,
        value,
        httponly=AUTH_COOKIE_HTTP_ONLY,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        secure=settings.AUTH_COOKIE_SECURE,
    )
