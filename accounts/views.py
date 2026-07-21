from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.cookies import (
    REFRESH_TOKEN_COOKIE_NAME,
    delete_auth_cookies,
    set_access_token_cookie,
    set_auth_cookies,
)
from accounts.emails import send_activation_email
from accounts.serializers import LoginSerializer, RegistrationSerializer


class RegisterView(APIView):
    """Create inactive users from public registration requests."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = default_token_generator.make_token(user)
        send_activation_email(request, user, token)
        return Response(
            {'user': {'id': user.id, 'email': user.email}, 'token': token},
            status=status.HTTP_201_CREATED,
        )


class ActivateView(APIView):
    """Activate a user account from an emailed activation link."""

    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        user = self._get_user(uidb64)
        if user is None or not default_token_generator.check_token(user, token):
            return Response(
                {'detail': 'Activation failed. The link may be invalid or expired.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.is_active = True
        user.save(update_fields=['is_active'])
        return Response({'message': 'Account successfully activated.'})

    @staticmethod
    def _get_user(uidb64):
        user_model = get_user_model()
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            return user_model.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, user_model.DoesNotExist):
            return None


class LoginView(APIView):
    """Authenticate a user by email and set JWT auth cookies."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        response = Response(
            {
                'detail': 'Login successful',
                'user': {'id': user.id, 'username': user.username},
            }
        )
        set_auth_cookies(response, str(refresh.access_token), str(refresh))
        return response


class LogoutView(APIView):
    """Blacklist the refresh token and clear both auth cookies."""

    permission_classes = [AllowAny]

    def post(self, request):
        raw_token = request.COOKIES.get(REFRESH_TOKEN_COOKIE_NAME)
        if raw_token is None:
            return Response(
                {'detail': 'Refresh token is missing.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            RefreshToken(raw_token).blacklist()
        except TokenError:
            return Response(
                {'detail': 'Invalid or expired refresh token.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        response = Response(
            {
                'detail': (
                    'Logout successful! All tokens will be deleted. '
                    'Refresh token is now invalid.'
                )
            }
        )
        delete_auth_cookies(response)
        return response


class TokenRefreshView(APIView):
    """Issue a new access token from the refresh token cookie."""

    permission_classes = [AllowAny]

    def post(self, request):
        raw_token = request.COOKIES.get(REFRESH_TOKEN_COOKIE_NAME)
        if raw_token is None:
            return Response(
                {'detail': 'Refresh token is missing.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return self._refreshed_response(raw_token)

    @staticmethod
    def _refreshed_response(raw_token):
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
