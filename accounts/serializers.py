"""Serializers validating the account request payloads.

Error messages are kept deliberately generic where a precise one would reveal
whether an email address is registered.
"""

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers


class RegistrationSerializer(serializers.Serializer):
    """Validate registration requests and create inactive users."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirmed_password = serializers.CharField(write_only=True)
    privacy_policy = serializers.BooleanField(required=False, default=False)

    def validate_email(self, value):
        """Reject an address that is taken, without saying that it is."""
        if get_user_model().objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Please check your input and try again.')
        return value

    def validate(self, attrs):
        """Check that both passwords match and satisfy Django's validators."""
        if attrs['password'] != attrs['confirmed_password']:
            raise serializers.ValidationError(
                {'confirmed_password': 'Passwords do not match.'}
            )
        validate_password(attrs['password'])
        return attrs

    def create(self, validated_data):
        """Create the account inactive; the activation email unlocks it."""
        accepted_at = timezone.now() if validated_data['privacy_policy'] else None
        return get_user_model().objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False,
            privacy_policy_accepted_at=accepted_at,
        )


class PasswordResetRequestSerializer(serializers.Serializer):
    """Validate the email format for a password reset request.

    Deliberately does not check whether the email belongs to an existing
    user: the view must respond identically either way to avoid leaking
    which addresses are registered.
    """

    email = serializers.EmailField()


class PasswordConfirmSerializer(serializers.Serializer):
    """Validate a new password pair for password reset confirmation."""

    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Check that both new passwords match and are strong enough."""
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError(
                {'confirm_password': 'Passwords do not match.'}
            )
        validate_password(attrs['new_password'])
        return attrs


class LoginSerializer(serializers.Serializer):
    """Validate login credentials by email and expose the authenticated user."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Authenticate the credentials and attach the user to the data.

        Inactive accounts and wrong passwords both end up here with the same
        message, so the response cannot be used to probe for accounts.
        """
        user = authenticate(
            request=self.context.get('request'),
            username=attrs['email'],
            password=attrs['password'],
        )
        if user is None:
            raise serializers.ValidationError('Invalid credentials.')
        attrs['user'] = user
        return attrs
