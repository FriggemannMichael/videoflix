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
def test_logout_with_valid_cookie_returns_200_and_clears_cookies(
    api_client, active_user
):
    refresh = RefreshToken.for_user(active_user)
    api_client.cookies[REFRESH_TOKEN_COOKIE_NAME] = str(refresh)
    api_client.cookies[ACCESS_TOKEN_COOKIE_NAME] = str(refresh.access_token)

    response = api_client.post(reverse('logout'))

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'detail': (
            'Logout successful! All tokens will be deleted. '
            'Refresh token is now invalid.'
        )
    }
    assert response.cookies[ACCESS_TOKEN_COOKIE_NAME].value == ''
    assert response.cookies[ACCESS_TOKEN_COOKIE_NAME]['max-age'] == 0
    assert response.cookies[REFRESH_TOKEN_COOKIE_NAME].value == ''
    assert response.cookies[REFRESH_TOKEN_COOKIE_NAME]['max-age'] == 0


@pytest.mark.django_db
def test_logout_blacklists_refresh_token(api_client, active_user):
    refresh = RefreshToken.for_user(active_user)
    api_client.cookies[REFRESH_TOKEN_COOKIE_NAME] = str(refresh)

    api_client.post(reverse('logout'))

    fresh_client = APIClient()
    fresh_client.cookies[REFRESH_TOKEN_COOKIE_NAME] = str(refresh)
    refresh_response = fresh_client.post(reverse('token_refresh'))

    assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED


def test_logout_without_refresh_cookie_returns_400(api_client):
    response = api_client.post(reverse('logout'))

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Refresh token is missing.'}


def test_logout_with_invalid_cookie_returns_401(api_client):
    api_client.cookies[REFRESH_TOKEN_COOKIE_NAME] = 'not-a-real-token'

    response = api_client.post(reverse('logout'))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Invalid or expired refresh token.'}
