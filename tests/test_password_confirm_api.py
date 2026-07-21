import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APIClient

RESET_CONFIRMED_DETAIL = 'Your Password has been successfully reset.'
RESET_INVALID_DETAIL = 'This password reset link is invalid or has expired.'


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def existing_user():
    return get_user_model().objects.create_user(
        username='user@example.com',
        email='user@example.com',
        password='Old-str0ng-pass!',
        is_active=True,
    )


def _confirm_url(user, token):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    return reverse('password_confirm', kwargs={'uidb64': uidb64, 'token': token})


@pytest.mark.django_db
def test_confirm_with_valid_token_resets_password(api_client, existing_user):
    token = default_token_generator.make_token(existing_user)

    response = api_client.post(
        _confirm_url(existing_user, token),
        {'new_password': 'New-str0ng-pass!', 'confirm_password': 'New-str0ng-pass!'},
        format='json',
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'detail': RESET_CONFIRMED_DETAIL}
    existing_user.refresh_from_db()
    assert existing_user.check_password('New-str0ng-pass!')


@pytest.mark.django_db
def test_confirm_rejects_invalid_token(api_client, existing_user):
    response = api_client.post(
        _confirm_url(existing_user, 'not-a-real-token'),
        {'new_password': 'New-str0ng-pass!', 'confirm_password': 'New-str0ng-pass!'},
        format='json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': RESET_INVALID_DETAIL}
    existing_user.refresh_from_db()
    assert existing_user.check_password('Old-str0ng-pass!')


@pytest.mark.django_db
def test_confirm_rejects_unknown_uid(api_client):
    uidb64 = urlsafe_base64_encode(force_bytes(999999))

    response = api_client.post(
        reverse('password_confirm', kwargs={'uidb64': uidb64, 'token': 'irrelevant'}),
        {'new_password': 'New-str0ng-pass!', 'confirm_password': 'New-str0ng-pass!'},
        format='json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': RESET_INVALID_DETAIL}


@pytest.mark.django_db
def test_confirm_rejects_password_mismatch(api_client, existing_user):
    token = default_token_generator.make_token(existing_user)

    response = api_client.post(
        _confirm_url(existing_user, token),
        {'new_password': 'New-str0ng-pass!', 'confirm_password': 'different-pass'},
        format='json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'confirm_password' in response.json()
    existing_user.refresh_from_db()
    assert existing_user.check_password('Old-str0ng-pass!')


@pytest.mark.django_db
def test_confirm_rejects_weak_password(api_client, existing_user):
    token = default_token_generator.make_token(existing_user)

    response = api_client.post(
        _confirm_url(existing_user, token),
        {'new_password': 'short', 'confirm_password': 'short'},
        format='json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    existing_user.refresh_from_db()
    assert existing_user.check_password('Old-str0ng-pass!')


@pytest.mark.django_db
def test_confirm_rejects_reused_token_after_password_change(api_client, existing_user):
    token = default_token_generator.make_token(existing_user)
    api_client.post(
        _confirm_url(existing_user, token),
        {'new_password': 'New-str0ng-pass!', 'confirm_password': 'New-str0ng-pass!'},
        format='json',
    )

    response = api_client.post(
        _confirm_url(existing_user, token),
        {'new_password': 'Another-pass1!', 'confirm_password': 'Another-pass1!'},
        format='json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': RESET_INVALID_DETAIL}
