"""A forged cross-site write is only worth something when cookies ride along."""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from accounts.cookies import ACCESS_TOKEN_COOKIE_NAME, REFRESH_TOKEN_COOKIE_NAME

pytestmark = pytest.mark.django_db

ALLOWED_ORIGINS = ('http://localhost:5500', 'http://127.0.0.1:5500')
FOREIGN_ORIGIN = 'http://evil.example.com'
PASSWORD = 'Str0ng-test-pass!'


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def credentials():
    get_user_model().objects.create_user(
        username='user@example.com',
        email='user@example.com',
        password=PASSWORD,
        is_active=True,
    )
    return {'email': 'user@example.com', 'password': PASSWORD}


def _login(api_client, credentials, **extra):
    return api_client.post(reverse('login'), credentials, format='json', **extra)


@pytest.mark.parametrize(
    'cookie_name', [ACCESS_TOKEN_COOKIE_NAME, REFRESH_TOKEN_COOKIE_NAME]
)
def test_post_carrying_a_cookie_from_a_foreign_origin_is_rejected(
    api_client, credentials, cookie_name
):
    api_client.cookies[cookie_name] = 'whatever-the-browser-still-holds'

    response = _login(api_client, credentials, HTTP_ORIGIN=FOREIGN_ORIGIN)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {'detail': 'Origin not allowed.'}
    assert 'access_token' not in response.cookies


def test_forged_logout_from_a_foreign_origin_is_rejected(api_client):
    """Logout revokes a token, so it is exactly the kind of write to protect."""
    api_client.cookies[REFRESH_TOKEN_COOKIE_NAME] = 'a-real-session-token'

    response = api_client.post(reverse('logout'), HTTP_ORIGIN=FOREIGN_ORIGIN)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_post_without_a_cookie_from_a_foreign_origin_is_allowed(api_client):
    """Registration carries no credentials, so there is nothing to forge.

    The frontend may be served from a port this project never anticipated;
    blocking it would break signing up without protecting anything.
    """
    response = api_client.post(
        reverse('register'),
        {
            'email': 'from-anywhere@example.com',
            'password': PASSWORD,
            'confirmed_password': PASSWORD,
        },
        format='json',
        HTTP_ORIGIN=FOREIGN_ORIGIN,
    )

    assert response.status_code == status.HTTP_201_CREATED


def test_login_without_a_cookie_from_a_foreign_origin_is_allowed(
    api_client, credentials
):
    response = _login(api_client, credentials, HTTP_ORIGIN=FOREIGN_ORIGIN)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize('origin', ALLOWED_ORIGINS)
def test_post_from_allowed_origin_succeeds(api_client, credentials, origin):
    api_client.cookies[ACCESS_TOKEN_COOKIE_NAME] = 'a-leftover-token'

    response = _login(api_client, credentials, HTTP_ORIGIN=origin)

    assert response.status_code == status.HTTP_200_OK


def test_post_without_origin_still_works(api_client, credentials):
    api_client.cookies[ACCESS_TOKEN_COOKIE_NAME] = 'a-leftover-token'

    response = _login(api_client, credentials)

    assert response.status_code == status.HTTP_200_OK


def test_same_origin_post_is_allowed(api_client, credentials):
    api_client.cookies[ACCESS_TOKEN_COOKIE_NAME] = 'a-leftover-token'

    response = _login(api_client, credentials, HTTP_ORIGIN='http://testserver')

    assert response.status_code == status.HTTP_200_OK


def test_get_from_foreign_origin_is_not_blocked(api_client):
    api_client.cookies[ACCESS_TOKEN_COOKIE_NAME] = 'a-leftover-token'

    response = api_client.get(reverse('video_list'), HTTP_ORIGIN=FOREIGN_ORIGIN)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_preflight_from_foreign_origin_is_not_blocked(api_client):
    response = api_client.options(
        reverse('login'),
        HTTP_ORIGIN=FOREIGN_ORIGIN,
        HTTP_ACCESS_CONTROL_REQUEST_METHOD='POST',
    )

    assert response.status_code != status.HTTP_403_FORBIDDEN
    assert 'Access-Control-Allow-Origin' not in response
