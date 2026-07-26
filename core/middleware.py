"""Origin-based CSRF protection for the cookie-authenticated API.

The auth cookies use ``SameSite=None`` so the provided frontend can reach the
API from a different host, which means the browser no longer refuses to attach
them to cross-site requests. Browsers do send an ``Origin`` header on those
requests and scripts cannot forge it, so checking it restores the protection
``SameSite`` used to provide. Non-browser clients (curl, Postman) send no
``Origin`` at all and are unaffected.

The check applies only to requests that actually carry an auth cookie. That is
the whole attack surface: forgery is worth something only when the browser
attaches credentials the attacker cannot read. A request without those cookies
has no privileges to abuse, so rejecting it would protect nothing while making
registration and login fail for anyone serving the frontend from an origin this
project did not anticipate. Django's own CSRF middleware still covers the
session cookie the admin uses.
"""

from django.conf import settings
from django.http import JsonResponse

from accounts.cookies import ACCESS_TOKEN_COOKIE_NAME, REFRESH_TOKEN_COOKIE_NAME

SAFE_METHODS = frozenset({'GET', 'HEAD', 'OPTIONS', 'TRACE'})
AUTH_COOKIE_NAMES = (ACCESS_TOKEN_COOKIE_NAME, REFRESH_TOKEN_COOKIE_NAME)


def own_origin(request):
    """Return the origin the request was addressed to, for same-origin posts."""
    return f'{request.scheme}://{request.get_host()}'


def carries_auth_cookie(request):
    """Report whether the browser attached credentials this request could abuse."""
    return any(name in request.COOKIES for name in AUTH_COOKIE_NAMES)


class TrustedOriginMiddleware:
    """Reject state-changing browser requests from an untrusted origin."""

    def __init__(self, get_response):
        """Store the next handler in the middleware chain."""
        self.get_response = get_response

    def __call__(self, request):
        """Pass the request on, or answer 403 for an untrusted origin."""
        if not self.is_trusted(request):
            return JsonResponse({'detail': 'Origin not allowed.'}, status=403)
        return self.get_response(request)

    def is_trusted(self, request):
        """Allow everything that cannot be a forged request against a session."""
        origin = request.headers.get('Origin')
        if request.method in SAFE_METHODS or origin is None:
            return True
        if not carries_auth_cookie(request):
            return True
        return origin in settings.CORS_ALLOWED_ORIGINS or origin == own_origin(request)
