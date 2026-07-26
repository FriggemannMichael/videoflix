"""Authentication backend that reads the JWT from a cookie.

Registered as the project-wide default authentication class, so every view is
authenticated the same way the provided frontend logs in.
"""

from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.cookies import ACCESS_TOKEN_COOKIE_NAME


class CookieJWTAuthentication(JWTAuthentication):
    """Authenticate requests using the access token stored in an HTTP-only cookie."""

    def authenticate(self, request):
        """Return the user and token, or None when the cookie is absent."""
        raw_token = request.COOKIES.get(ACCESS_TOKEN_COOKIE_NAME)
        if raw_token is None:
            return None
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
