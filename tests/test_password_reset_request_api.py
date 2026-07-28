import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

RESET_SENT_DETAIL = 'An email has been sent to reset your password.'


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def existing_user():
    return get_user_model().objects.create_user(
        username='user@example.com',
        email='user@example.com',
        password='Str0ng-test-pass!',
        is_active=True,
    )


@pytest.mark.django_db
def test_returns_200_and_sends_email_for_existing_account(api_client, existing_user):
    response = api_client.post(
        reverse('password_reset'), {'email': 'user@example.com'}, format='json'
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'detail': RESET_SENT_DETAIL}
    assert len(mail.outbox) == 1
    email = mail.outbox[0]
    assert email.to == ['user@example.com']
    assert 'confirm_password.html?uid=' in email.body


@pytest.mark.django_db
def test_returns_identical_response_for_unknown_email(api_client):
    response = api_client.post(
        reverse('password_reset'), {'email': 'unknown@example.com'}, format='json'
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'detail': RESET_SENT_DETAIL}
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_rejects_invalid_email_format(api_client):
    response = api_client.post(
        reverse('password_reset'), {'email': 'not-an-email'}, format='json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_reset_link_contains_valid_uid_and_token(api_client, existing_user, settings):
    settings.FRONTEND_EMAIL_LINK_URL = 'http://127.0.0.1:5500'

    api_client.post(
        reverse('password_reset'), {'email': 'user@example.com'}, format='json'
    )

    email = mail.outbox[0]
    assert 'http://127.0.0.1:5500/pages/auth/confirm_password.html?uid=' in email.body
    assert '&token=' in email.body
