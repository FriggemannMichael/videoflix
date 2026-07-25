"""Guard the settings the provided frontend depends on.

The frontend is served from ``localhost:5500`` but calls the API on
``127.0.0.1:8000``. That is a cross-site request, so both the CORS origins and
the auth cookie flags have to allow it, otherwise the dashboard silently shows
no videos.
"""

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from accounts.cookies import ACCESS_TOKEN_COOKIE_NAME, REFRESH_TOKEN_COOKIE_NAME

FRONTEND_ORIGINS = ('http://localhost:5500', 'http://127.0.0.1:5500')


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


@pytest.mark.parametrize('origin', FRONTEND_ORIGINS)
def test_both_frontend_origins_are_allowed(origin):
    assert origin in settings.CORS_ALLOWED_ORIGINS


def test_frontend_url_is_always_an_allowed_origin():
    assert settings.FRONTEND_URL in settings.CORS_ALLOWED_ORIGINS


def test_credentials_are_allowed_so_cookies_can_be_sent():
    assert settings.CORS_ALLOW_CREDENTIALS is True


@pytest.mark.parametrize('origin', FRONTEND_ORIGINS)
@pytest.mark.django_db
def test_preflight_from_frontend_origin_is_accepted(api_client, origin):
    response = api_client.options(
        reverse('video_list'),
        HTTP_ORIGIN=origin,
        HTTP_ACCESS_CONTROL_REQUEST_METHOD='GET',
    )

    assert response['Access-Control-Allow-Origin'] == origin
    assert response['Access-Control-Allow-Credentials'] == 'true'


@pytest.mark.django_db
def test_auth_cookies_are_sent_cross_site(api_client, active_user):
    response = api_client.post(
        reverse('login'),
        {'email': 'user@example.com', 'password': 'Str0ng-test-pass!'},
        format='json',
    )

    assert response.status_code == status.HTTP_200_OK
    for name in (ACCESS_TOKEN_COOKIE_NAME, REFRESH_TOKEN_COOKIE_NAME):
        cookie = response.cookies[name]
        assert cookie['samesite'] == 'None'
        assert cookie['secure'] is True
        assert cookie['httponly'] is True
