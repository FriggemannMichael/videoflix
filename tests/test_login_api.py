import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


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
def test_login_with_valid_credentials_returns_200_and_sets_cookies(
    api_client, active_user
):
    response = api_client.post(
        reverse('login'),
        {'email': 'user@example.com', 'password': 'Str0ng-test-pass!'},
        format='json',
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'detail': 'Login successful',
        'user': {'id': active_user.id, 'username': 'user@example.com'},
    }
    assert 'access_token' in response.cookies
    assert 'refresh_token' in response.cookies


@pytest.mark.django_db
def test_login_does_not_expose_tokens_in_response_body(api_client, active_user):
    response = api_client.post(
        reverse('login'),
        {'email': 'user@example.com', 'password': 'Str0ng-test-pass!'},
        format='json',
    )

    body = response.json()
    assert 'access' not in body
    assert 'refresh' not in body
    assert 'token' not in body


@pytest.mark.django_db
def test_login_cookies_are_httponly(api_client, active_user):
    response = api_client.post(
        reverse('login'),
        {'email': 'user@example.com', 'password': 'Str0ng-test-pass!'},
        format='json',
    )

    assert response.cookies['access_token']['httponly'] is True
    assert response.cookies['refresh_token']['httponly'] is True


@pytest.mark.django_db
def test_login_with_wrong_password_returns_401(api_client, active_user):
    response = api_client.post(
        reverse('login'),
        {'email': 'user@example.com', 'password': 'wrong-password'},
        format='json',
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Invalid credentials.'}
    assert 'access_token' not in response.cookies


@pytest.mark.django_db
def test_login_with_unknown_email_returns_401(api_client):
    response = api_client.post(
        reverse('login'),
        {'email': 'nobody@example.com', 'password': 'Str0ng-test-pass!'},
        format='json',
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_login_rejects_invalid_email_format_with_400(api_client):
    response = api_client.post(
        reverse('login'),
        {'email': 'not-an-email', 'password': 'irrelevant'},
        format='json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'access_token' not in response.cookies


@pytest.mark.django_db
def test_login_rejects_missing_password_with_400(api_client, active_user):
    response = api_client.post(
        reverse('login'), {'email': 'user@example.com'}, format='json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'password' in response.json()


@pytest.mark.django_db
def test_login_with_inactive_account_returns_401(api_client):
    get_user_model().objects.create_user(
        username='pending@example.com',
        email='pending@example.com',
        password='Str0ng-test-pass!',
        is_active=False,
    )

    response = api_client.post(
        reverse('login'),
        {'email': 'pending@example.com', 'password': 'Str0ng-test-pass!'},
        format='json',
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Invalid credentials.'}
