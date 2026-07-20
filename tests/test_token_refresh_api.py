import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.cookies import ACCESS_TOKEN_COOKIE_NAME, REFRESH_TOKEN_COOKIE_NAME


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


@pytest.mark.django_db
def test_refresh_with_valid_cookie_returns_200_and_new_access_cookie(
    api_client, active_user
):
    refresh = RefreshToken.for_user(active_user)
    api_client.cookies[REFRESH_TOKEN_COOKIE_NAME] = str(refresh)

    response = api_client.post(reverse('token_refresh'))

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body['detail'] == 'Token refreshed'
    assert isinstance(body['access'], str) and body['access']
    assert ACCESS_TOKEN_COOKIE_NAME in response.cookies
    assert response.cookies[ACCESS_TOKEN_COOKIE_NAME]['httponly'] is True
    assert response.cookies[ACCESS_TOKEN_COOKIE_NAME].value == body['access']


@pytest.mark.django_db
def test_refresh_does_not_touch_refresh_cookie(api_client, active_user):
    refresh = RefreshToken.for_user(active_user)
    api_client.cookies[REFRESH_TOKEN_COOKIE_NAME] = str(refresh)

    response = api_client.post(reverse('token_refresh'))

    assert REFRESH_TOKEN_COOKIE_NAME not in response.cookies


def test_refresh_without_cookie_returns_400(api_client):
    response = api_client.post(reverse('token_refresh'))

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert ACCESS_TOKEN_COOKIE_NAME not in response.cookies


def test_refresh_with_invalid_cookie_returns_401(api_client):
    api_client.cookies[REFRESH_TOKEN_COOKIE_NAME] = 'not-a-real-token'

    response = api_client.post(reverse('token_refresh'))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert ACCESS_TOKEN_COOKIE_NAME not in response.cookies
