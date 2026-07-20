import pytest
from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

pytestmark = pytest.mark.django_db


def test_accounts_app_is_registered():
    assert apps.is_installed('accounts')


def test_auth_user_model_points_to_accounts_user():
    assert get_user_model().__module__ == 'accounts.models'
    assert get_user_model().__name__ == 'User'


def test_regular_user_can_be_created():
    user = get_user_model().objects.create_user(
        username='user@example.com',
        email='user@example.com',
        password='securepassword',
    )

    assert user.pk is not None
    assert user.check_password('securepassword')
    assert user.is_active is True


def test_superuser_can_be_created():
    user = get_user_model().objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpassword',
    )

    assert user.is_staff is True
    assert user.is_superuser is True


def test_email_must_be_unique():
    get_user_model().objects.create_user(
        username='first', email='dup@example.com', password='securepassword'
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        get_user_model().objects.create_user(
            username='second', email='dup@example.com', password='securepassword'
        )


def test_privacy_policy_accepted_at_defaults_to_none():
    user = get_user_model().objects.create_user(
        username='user2', email='user2@example.com', password='securepassword'
    )

    assert user.privacy_policy_accepted_at is None


def test_user_is_registered_in_admin():
    from django.contrib import admin

    assert admin.site.is_registered(get_user_model())
