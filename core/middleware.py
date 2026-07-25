"""Origin-based CSRF protection for the cookie-authenticated API.

The auth cookies use ``SameSite=None`` so the provided frontend can reach the
API from a different host, which means the browser no longer refuses to attach
them to cross-site requests. Browsers do send an ``Origin`` header on those
requests and scripts cannot forge it, so checking it restores the protection
``SameSite`` used to provide. Non-browser clients (curl, Postman) send no
``Origin`` at all and are unaffected.
"""

from django.conf import settings
from django.http import JsonResponse

SAFE_METHODS = frozenset({'GET', 'HEAD', 'OPTIONS', 'TRACE'})


def own_origin(request):
    """Return the origin the request was addressed to, for same-origin posts."""
    return f'{request.scheme}://{request.get_host()}'


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
        """Allow safe methods, clients without an origin, and known origins."""
        origin = request.headers.get('Origin')
        if request.method in SAFE_METHODS or origin is None:
            return True
        return origin in settings.CORS_ALLOWED_ORIGINS or origin == own_origin(request)
