import pytest
from django.conf import settings as django_settings
from django.contrib.auth import get_user_model

from accounts.emails import build_activation_link, build_password_reset_link


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user(
        username='link-user@example.com',
        email='link-user@example.com',
        password='Str0ng-test-pass!',
    )


def test_cors_allowed_origins_is_a_list_of_origins():
    assert isinstance(django_settings.CORS_ALLOWED_ORIGINS, list)
    assert django_settings.CORS_ALLOWED_ORIGINS
    for origin in django_settings.CORS_ALLOWED_ORIGINS:
        assert origin.startswith('http://') or origin.startswith('https://')


def test_email_link_url_has_no_trailing_slash():
    assert not django_settings.FRONTEND_EMAIL_LINK_URL.endswith('/')


def test_email_links_use_the_email_link_url(user, settings):
    settings.FRONTEND_EMAIL_LINK_URL = 'https://videoflix.example'

    assert build_activation_link(user, 'token').startswith(
        'https://videoflix.example/pages/auth/'
    )
    assert build_password_reset_link(user, 'token').startswith(
        'https://videoflix.example/pages/auth/'
    )


def test_email_link_url_does_not_define_the_cors_allow_list(settings):
    origins = list(settings.CORS_ALLOWED_ORIGINS)

    settings.FRONTEND_EMAIL_LINK_URL = 'https://videoflix.example'

    assert settings.CORS_ALLOWED_ORIGINS == origins
    assert 'https://videoflix.example' not in settings.CORS_ALLOWED_ORIGINS
