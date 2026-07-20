ACCESS_TOKEN_COOKIE_NAME = 'access_token'
REFRESH_TOKEN_COOKIE_NAME = 'refresh_token'
AUTH_COOKIE_HTTP_ONLY = True
AUTH_COOKIE_SAMESITE = 'Lax'
AUTH_COOKIE_SECURE = False


def set_auth_cookies(response, access_token, refresh_token):
    """Attach both the access and refresh token cookies to the response."""
    set_access_token_cookie(response, access_token)
    _set_cookie(response, REFRESH_TOKEN_COOKIE_NAME, refresh_token)


def set_access_token_cookie(response, access_token):
    """Store a (refreshed) access token as an HTTP-only cookie on the response."""
    _set_cookie(response, ACCESS_TOKEN_COOKIE_NAME, access_token)


def _set_cookie(response, name, value):
    """Write a single HTTP-only auth cookie with the shared security flags."""
    response.set_cookie(
        name,
        value,
        httponly=AUTH_COOKIE_HTTP_ONLY,
        samesite=AUTH_COOKIE_SAMESITE,
        secure=AUTH_COOKIE_SECURE,
    )
