from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers


class RegistrationSerializer(serializers.Serializer):
    """Validate registration requests and create inactive users."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirmed_password = serializers.CharField(write_only=True)
    privacy_policy = serializers.BooleanField()

    def validate_email(self, value):
        if get_user_model().objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('A user with that email already exists.')
        return value

    def validate_privacy_policy(self, value):
        if not value:
            raise serializers.ValidationError('You must accept the privacy policy.')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['confirmed_password']:
            raise serializers.ValidationError(
                {'confirmed_password': 'Passwords do not match.'}
            )
        validate_password(attrs['password'])
        return attrs

    def create(self, validated_data):
        return get_user_model().objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False,
            privacy_policy_accepted_at=timezone.now(),
        )
