"""Cross-site requests carry the auth cookies, so the origin has to be checked."""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db

ALLOWED_ORIGINS = ('http://localhost:5500', 'http://127.0.0.1:5500')
FOREIGN_ORIGIN = 'http://evil.example.com'


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def credentials():
    get_user_model().objects.create_user(
        username='user@example.com',
        email='user@example.com',
        password='Str0ng-test-pass!',
        is_active=True,
    )
    return {'email': 'user@example.com', 'password': 'Str0ng-test-pass!'}


def _login(api_client, credentials, **extra):
    return api_client.post(reverse('login'), credentials, format='json', **extra)


def test_post_from_foreign_origin_is_rejected(api_client, credentials):
    response = _login(api_client, credentials, HTTP_ORIGIN=FOREIGN_ORIGIN)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {'detail': 'Origin not allowed.'}
    assert 'access_token' not in response.cookies


@pytest.mark.parametrize('origin', ALLOWED_ORIGINS)
def test_post_from_allowed_origin_succeeds(api_client, credentials, origin):
    response = _login(api_client, credentials, HTTP_ORIGIN=origin)

    assert response.status_code == status.HTTP_200_OK


def test_post_without_origin_still_works(api_client, credentials):
    response = _login(api_client, credentials)

    assert response.status_code == status.HTTP_200_OK


def test_same_origin_post_is_allowed(api_client, credentials):
    response = _login(api_client, credentials, HTTP_ORIGIN='http://testserver')

    assert response.status_code == status.HTTP_200_OK


def test_get_from_foreign_origin_is_not_blocked(api_client):
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
