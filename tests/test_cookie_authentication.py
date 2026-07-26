from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from accounts.cookies import ACCESS_TOKEN_COOKIE_NAME

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def active_user():
    return get_user_model().objects.create_user(
        username='user@example.com',
        email='user@example.com',
        password='Str0ng-test-pass!',
        is_active=True,
    )


@pytest.fixture
def registration_payload():
    return {
        'email': 'new-user@example.com',
        'password': 'Str0ng-test-pass!',
        'confirmed_password': 'Str0ng-test-pass!',
    }


def expired_token(user):
    """Return a structurally valid access token that has already expired."""
    token = AccessToken.for_user(user)
    token.set_exp(lifetime=timedelta(seconds=-1))
    return str(token)


@pytest.mark.parametrize(
    'raw_token',
    ['not-a-jwt', ''],
    ids=['garbage', 'empty'],
)
def test_register_ignores_an_unusable_access_token_cookie(
    api_client, registration_payload, raw_token
):
    api_client.cookies[ACCESS_TOKEN_COOKIE_NAME] = raw_token

    response = api_client.post(reverse('register'), registration_payload, format='json')

    assert response.status_code == status.HTTP_201_CREATED


def test_register_ignores_an_expired_access_token_cookie(
    api_client, active_user, registration_payload
):
    api_client.cookies[ACCESS_TOKEN_COOKIE_NAME] = expired_token(active_user)

    response = api_client.post(reverse('register'), registration_payload, format='json')

    assert response.status_code == status.HTTP_201_CREATED


def test_register_ignores_a_token_of_a_deleted_user(
    api_client, active_user, registration_payload
):
    """A reset database leaves cookies behind that point at a gone user."""
    api_client.cookies[ACCESS_TOKEN_COOKIE_NAME] = str(
        RefreshToken.for_user(active_user).access_token
    )
    active_user.delete()

    response = api_client.post(reverse('register'), registration_payload, format='json')

    assert response.status_code == status.HTTP_201_CREATED


def test_login_ignores_an_expired_access_token_cookie(api_client, active_user):
    api_client.cookies[ACCESS_TOKEN_COOKIE_NAME] = expired_token(active_user)

    response = api_client.post(
        reverse('login'),
        {'email': active_user.email, 'password': 'Str0ng-test-pass!'},
        format='json',
    )

    assert response.status_code == status.HTTP_200_OK


def test_password_reset_ignores_an_expired_access_token_cookie(api_client, active_user):
    api_client.cookies[ACCESS_TOKEN_COOKIE_NAME] = expired_token(active_user)

    response = api_client.post(
        reverse('password_reset'), {'email': active_user.email}, format='json'
    )

    assert response.status_code == status.HTTP_200_OK


def test_protected_view_still_rejects_an_expired_access_token_cookie(
    api_client, active_user
):
    api_client.cookies[ACCESS_TOKEN_COOKIE_NAME] = expired_token(active_user)

    response = api_client.get(reverse('video_list'))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_protected_view_still_rejects_a_token_of_a_deleted_user(
    api_client, active_user
):
    api_client.cookies[ACCESS_TOKEN_COOKIE_NAME] = str(
        RefreshToken.for_user(active_user).access_token
    )
    active_user.delete()

    response = api_client.get(reverse('video_list'))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_protected_view_still_accepts_a_valid_access_token_cookie(
    api_client, active_user
):
    api_client.cookies[ACCESS_TOKEN_COOKIE_NAME] = str(
        RefreshToken.for_user(active_user).access_token
    )

    response = api_client.get(reverse('video_list'))

    assert response.status_code == status.HTTP_200_OK
