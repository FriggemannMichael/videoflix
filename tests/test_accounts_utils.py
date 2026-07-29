import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from accounts.utils import get_user_from_uidb64, send_reset_email_if_user_exists


@pytest.fixture
def existing_user():
    return get_user_model().objects.create_user(
        username='user@example.com',
        email='user@example.com',
        password='Str0ng-test-pass!',
        is_active=True,
    )


@pytest.mark.django_db
def test_get_user_from_uidb64_returns_user_for_valid_uid(existing_user):
    uidb64 = urlsafe_base64_encode(force_bytes(existing_user.pk))

    assert get_user_from_uidb64(uidb64) == existing_user


def test_get_user_from_uidb64_returns_none_for_malformed_uid():
    assert get_user_from_uidb64('not-valid-base64!!!') is None


@pytest.mark.django_db
def test_get_user_from_uidb64_returns_none_for_unknown_id():
    uidb64 = urlsafe_base64_encode(force_bytes(999999))

    assert get_user_from_uidb64(uidb64) is None


@pytest.mark.django_db
def test_send_reset_email_if_user_exists_sends_email(existing_user):
    send_reset_email_if_user_exists('user@example.com')

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ['user@example.com']


@pytest.mark.django_db
def test_send_reset_email_if_user_exists_is_a_noop_for_unknown_email():
    send_reset_email_if_user_exists('unknown@example.com')

    assert len(mail.outbox) == 0
