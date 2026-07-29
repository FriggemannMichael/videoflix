"""API views for registration, login, logout, and password recovery.

Every view returns a response and delegates the rest to serializers, to
``accounts.utils``, and to ``accounts.cookies``. Tokens are never handed to
the client in a readable form; they are set as HTTP-only cookies.
"""

from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.api.serializers import (
    LoginSerializer,
    PasswordConfirmSerializer,
    PasswordResetRequestSerializer,
    RegistrationSerializer,
)
from accounts.cookies import (
    REFRESH_TOKEN_COOKIE_NAME,
    delete_auth_cookies,
    set_access_token_cookie,
    set_auth_cookies,
)
from accounts.emails import send_activation_email
from accounts.utils import get_user_from_uidb64, send_reset_email_if_user_exists


class RegisterView(APIView):
    """Create inactive users from public registration requests.

    Creating the user and sending the activation mail share one transaction:
    a failing mail server rolls the user back instead of leaving behind an
    account that nobody can ever activate.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """Register the account and mail its activation link."""
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            user = serializer.save()
            token = default_token_generator.make_token(user)
            send_activation_email(user, token)
        return Response(
            {'user': {'id': user.id, 'email': user.email}, 'token': token},
            status=status.HTTP_201_CREATED,
        )


class ActivateView(APIView):
    """Activate a user account from an emailed activation link."""

    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        """Activate the account if the link is intact and still valid."""
        user = get_user_from_uidb64(uidb64)
        if user is None or not default_token_generator.check_token(user, token):
            return Response(
                {'detail': 'Activation failed. The link may be invalid or expired.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.is_active = True
        user.save(update_fields=['is_active'])
        return Response({'message': 'Account successfully activated.'})


LOGIN_FAILED_DETAIL = 'Invalid credentials.'


class LoginView(APIView):
    """Authenticate a user by email and set JWT auth cookies.

    A well formed payload whose credentials do not match is answered with an
    explicit 401 rather than a raised authentication exception: DRF turns
    such an exception into a 403 unless the first authenticator sends a
    ``WWW-Authenticate`` header, which cookie authentication does not.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """Log the user in and hand out both tokens as cookies."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self._authenticate(request, serializer.validated_data)
        if user is None:
            return Response(
                {'detail': LOGIN_FAILED_DETAIL},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return self._login_response(user)

    @staticmethod
    def _authenticate(request, credentials):
        """Return the user behind the credentials, or None if they do not match.

        Inactive accounts and wrong passwords are both answered with the same
        generic detail, so the response cannot be used to probe for accounts.
        """
        return authenticate(
            request=request,
            username=credentials['email'],
            password=credentials['password'],
        )

    @staticmethod
    def _login_response(user):
        """Answer with the user and set both tokens as cookies."""
        refresh = RefreshToken.for_user(user)
        response = Response(
            {
                'detail': 'Login successful',
                'user': {'id': user.id, 'username': user.username},
            }
        )
        set_auth_cookies(response, str(refresh.access_token), str(refresh))
        return response


LOGOUT_SUCCESS_DETAIL = (
    'Logout successful! All tokens will be deleted. Refresh token is now invalid.'
)


class LogoutView(APIView):
    """Blacklist the refresh token and clear both auth cookies."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Revoke the refresh token from the cookie and clear both cookies.

        Without that cookie there is nothing to revoke, so the request is
        rejected as a bad request.
        """
        raw_token = request.COOKIES.get(REFRESH_TOKEN_COOKIE_NAME)
        if raw_token is None:
            return Response(
                {'detail': 'Refresh token is missing.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return self._logout_response(raw_token)

    @staticmethod
    def _logout_response(raw_token):
        """Blacklist the refresh token and clear the cookies."""
        try:
            RefreshToken(raw_token).blacklist()
        except TokenError:
            return Response(
                {'detail': 'Invalid or expired refresh token.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        response = Response({'detail': LOGOUT_SUCCESS_DETAIL})
        delete_auth_cookies(response)
        return response


class TokenRefreshView(APIView):
    """Issue a new access token from the refresh token cookie.

    Answers with an explicit 401 rather than raising: DRF turns an
    authentication exception into a 403 unless the first authenticator sends
    a ``WWW-Authenticate`` header, which cookie authentication does not.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """Exchange the refresh token cookie for a fresh access token."""
        raw_token = request.COOKIES.get(REFRESH_TOKEN_COOKIE_NAME)
        if raw_token is None:
            return Response(
                {'detail': 'Refresh token is missing.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return self._refreshed_response(raw_token)

    @staticmethod
    def _refreshed_response(raw_token):
        """Answer with a new access token, also set as a cookie."""
        try:
            refresh = RefreshToken(raw_token)
        except TokenError:
            return Response(
                {'detail': 'Invalid or expired refresh token.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        access_token = str(refresh.access_token)
        response = Response({'detail': 'Token refreshed', 'access': access_token})
        set_access_token_cookie(response, access_token)
        return response


PASSWORD_RESET_SENT_DETAIL = 'An email has been sent to reset your password.'


class PasswordResetRequestView(APIView):
    """Send a password reset email without revealing whether the address exists."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Answer identically whether or not the address is registered."""
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        send_reset_email_if_user_exists(email)
        return Response({'detail': PASSWORD_RESET_SENT_DETAIL})


PASSWORD_RESET_CONFIRMED_DETAIL = 'Your Password has been successfully reset.'
PASSWORD_RESET_INVALID_DETAIL = 'This password reset link is invalid or has expired.'


class PasswordConfirmView(APIView):
    """Set a new password from a valid password reset link."""

    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        """Set the new password once the reset link checks out."""
        user = get_user_from_uidb64(uidb64)
        if user is None or not default_token_generator.check_token(user, token):
            return Response(
                {'detail': PASSWORD_RESET_INVALID_DETAIL},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return self._reset_password(user, request.data)

    @staticmethod
    def _reset_password(user, data):
        """Store the new password, which also invalidates the used link."""
        serializer = PasswordConfirmSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data['new_password'])
        user.save(update_fields=['password'])
        return Response({'detail': PASSWORD_RESET_CONFIRMED_DETAIL})
