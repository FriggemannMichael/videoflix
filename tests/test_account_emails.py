import pytest
from django.contrib.auth import get_user_model
from django.core import mail

from accounts.emails import (
    LOGO_CID,
    LOGO_PATH,
    send_activation_email,
    send_password_reset_email,
)


@pytest.fixture
def user():
    return get_user_model().objects.create_user(
        username='user@example.com',
        email='user@example.com',
        password='Str0ng-test-pass!',
        is_active=True,
    )


def image_parts(message):
    return [part for part in message.walk() if part.get_content_maintype() == 'image']


def only_logo_part(sent_email):
    parts = image_parts(sent_email.message())
    assert len(parts) == 1
    return parts[0]


@pytest.mark.django_db
@pytest.mark.parametrize(
    'send_email', [send_activation_email, send_password_reset_email]
)
def test_email_carries_the_logo_as_an_inline_part(user, send_email):
    send_email(user, 'token-123')

    logo = only_logo_part(mail.outbox[0])
    assert logo['Content-ID'] == f'<{LOGO_CID}>'
    assert logo.get_content_subtype() == 'png'
    assert logo.get_payload(decode=True) == LOGO_PATH.read_bytes()


@pytest.mark.django_db
@pytest.mark.parametrize(
    'send_email', [send_activation_email, send_password_reset_email]
)
def test_email_html_addresses_the_logo_by_content_id(user, send_email):
    send_email(user, 'token-123')

    html_body = mail.outbox[0].alternatives[0][0]
    assert f'src="cid:{LOGO_CID}"' in html_body


@pytest.mark.django_db
@pytest.mark.parametrize(
    'send_email', [send_activation_email, send_password_reset_email]
)
def test_email_html_does_not_link_the_logo_from_this_server(user, send_email):
    send_email(user, 'token-123')

    html_body = mail.outbox[0].alternatives[0][0]
    assert '/static/' not in html_body
    assert 'src="http' not in html_body


@pytest.mark.django_db
@pytest.mark.parametrize(
    'send_email', [send_activation_email, send_password_reset_email]
)
def test_email_relates_the_inline_part_to_the_html_body(user, send_email):
    send_email(user, 'token-123')

    message = mail.outbox[0].message()
    assert message.get_content_subtype() == 'related'
    assert only_logo_part(mail.outbox[0])['Content-Disposition'].startswith('inline')


@pytest.mark.django_db
@pytest.mark.parametrize(
    'send_email', [send_activation_email, send_password_reset_email]
)
def test_email_still_offers_a_plain_text_body(user, send_email):
    send_email(user, 'token-123')

    sent_email = mail.outbox[0]
    assert sent_email.body.strip()
    assert sent_email.alternatives[0][1] == 'text/html'
