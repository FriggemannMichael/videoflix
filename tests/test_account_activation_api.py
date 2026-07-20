import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def inactive_user():
    return get_user_model().objects.create_user(
        username='pending@example.com',
        email='pending@example.com',
        password='Str0ng-test-pass!',
        is_active=False,
    )


def _activation_url(user, token):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    return reverse('activate', kwargs={'uidb64': uidb64, 'token': token})


@pytest.mark.django_db
def test_activate_with_valid_token_activates_user(api_client, inactive_user):
    token = default_token_generator.make_token(inactive_user)

    response = api_client.get(_activation_url(inactive_user, token))

    inactive_user.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'message': 'Account successfully activated.'}
    assert inactive_user.is_active is True


@pytest.mark.django_db
def test_activate_with_invalid_token_returns_400(api_client, inactive_user):
    response = api_client.get(_activation_url(inactive_user, 'not-a-real-token'))

    inactive_user.refresh_from_db()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert inactive_user.is_active is False


@pytest.mark.django_db
def test_activate_with_unknown_user_returns_400(api_client):
    bogus_uidb64 = urlsafe_base64_encode(force_bytes(999999))

    response = api_client.get(
        reverse('activate', kwargs={'uidb64': bogus_uidb64, 'token': 'irrelevant'})
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_activate_with_malformed_uid_returns_400(api_client):
    response = api_client.get(
        reverse('activate', kwargs={'uidb64': 'not-base64!!', 'token': 'irrelevant'})
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_activate_is_idempotent_for_already_active_user(api_client, inactive_user):
    token = default_token_generator.make_token(inactive_user)
    api_client.get(_activation_url(inactive_user, token))

    response = api_client.get(_activation_url(inactive_user, token))

    assert response.status_code == status.HTTP_200_OK
