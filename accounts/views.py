from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.emails import send_activation_email
from accounts.serializers import RegistrationSerializer


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
