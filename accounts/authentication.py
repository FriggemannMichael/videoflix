"""Authentication backend that reads the JWT from a cookie.

Registered as the project-wide default authentication class, so every view is
authenticated the same way the provided frontend logs in.

A cookie is ambient: the browser attaches it to every request, including the
public ones that need no login at all. An unusable cookie therefore must not
fail the request, or a single leftover cookie -- an expired token, or one issued
before the database was reset -- would lock the user out of registering, logging
in, and resetting their password until they clear their browser storage by hand.
"""

from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.cookies import ACCESS_TOKEN_COOKIE_NAME


class CookieJWTAuthentication(JWTAuthentication):
    """Authenticate requests using the access token stored in an HTTP-only cookie."""

    def authenticate(self, request):
        """Return the user and token, or None when the cookie cannot be used.

        An unusable cookie leaves the request anonymous rather than failing it,
        so protected views still answer 401 through their permission class while
        the public ones keep working. See the module docstring for why.
        """
        raw_token = request.COOKIES.get(ACCESS_TOKEN_COOKIE_NAME)
        if raw_token is None:
            return None
        try:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except AuthenticationFailed:
            # Covers both an invalid or expired token and a token whose user no
            # longer exists, e.g. after the database has been reset.
            return None
