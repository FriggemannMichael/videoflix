import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def valid_payload():
    return {
        'email': 'new-user@example.com',
        'password': 'Str0ng-test-pass!',
        'confirmed_password': 'Str0ng-test-pass!',
        'privacy_policy': True,
    }


@pytest.mark.django_db
def test_register_creates_inactive_user(api_client, valid_payload):
    response = api_client.post(reverse('register'), valid_payload, format='json')

    user = get_user_model().objects.get(email='new-user@example.com')
    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body['user'] == {'id': user.id, 'email': user.email}
    assert 'token' in body
    assert user.check_password('Str0ng-test-pass!')
    assert user.is_active is False
    assert user.privacy_policy_accepted_at is not None


@pytest.mark.django_db
def test_register_rejects_password_mismatch(api_client, valid_payload):
    valid_payload['confirmed_password'] = 'different-pass'

    response = api_client.post(reverse('register'), valid_payload, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'confirmed_password' in response.json()
    assert not get_user_model().objects.filter(email='new-user@example.com').exists()


@pytest.mark.django_db
def test_register_rejects_duplicate_email(api_client, valid_payload):
    get_user_model().objects.create_user(
        username='existing@example.com',
        email='existing@example.com',
        password='Str0ng-test-pass!',
    )
    valid_payload['email'] = 'existing@example.com'

    response = api_client.post(reverse('register'), valid_payload, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'email' in response.json()


@pytest.mark.django_db
def test_register_rejects_declined_privacy_policy(api_client, valid_payload):
    valid_payload['privacy_policy'] = False

    response = api_client.post(reverse('register'), valid_payload, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'privacy_policy' in response.json()
    assert not get_user_model().objects.filter(email='new-user@example.com').exists()


@pytest.mark.django_db
def test_register_rejects_weak_password(api_client, valid_payload):
    valid_payload['password'] = 'short'
    valid_payload['confirmed_password'] = 'short'

    response = api_client.post(reverse('register'), valid_payload, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not get_user_model().objects.filter(email='new-user@example.com').exists()
