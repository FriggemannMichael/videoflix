from django.contrib.auth.tokens import default_token_generator
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers import RegistrationSerializer


class RegisterView(APIView):
    """Create inactive users from public registration requests."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = default_token_generator.make_token(user)
        return Response(
            {'user': {'id': user.id, 'email': user.email}, 'token': token},
            status=status.HTTP_201_CREATED,
        )
