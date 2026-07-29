"""Composing and sending the transactional account emails.

Both the activation and the password reset mail are sent as multipart
messages: a plain text body plus an HTML alternative rendered from the
templates in ``accounts/templates/accounts/``. The links they contain point
into the frontend, not the API, because the user finishes the flow there.

The logo travels inside the message as an inline part the HTML references by
content ID. Linking it as a URL instead would leave the image broken in every
mail client that cannot reach this backend.
"""

from email.mime.image import MIMEImage
from pathlib import Path

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

LOGO_CID = 'videoflix-logo'
LOGO_PATH = Path(__file__).resolve().parent / 'static' / 'accounts' / 'img' / 'logo.png'


def build_activation_link(user, token):
    """Build the frontend URL that activates the given user's account."""
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    path = f'/pages/auth/activate.html?uid={uidb64}&token={token}'
    return f'{settings.FRONTEND_EMAIL_LINK_URL}{path}'


def build_password_reset_link(user, token):
    """Build the frontend URL where the given user can set a new password."""
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    path = f'/pages/auth/confirm_password.html?uid={uidb64}&token={token}'
    return f'{settings.FRONTEND_EMAIL_LINK_URL}{path}'


def _inline_logo():
    """Return the logo as an inline part the HTML body addresses by its CID."""
    logo = MIMEImage(LOGO_PATH.read_bytes(), _subtype='png')
    logo.add_header('Content-ID', f'<{LOGO_CID}>')
    logo.add_header('Content-Disposition', 'inline', filename=LOGO_PATH.name)
    return logo


def _email_context(user, token):
    """Build the template context of the activation email."""
    return {
        'activation_link': build_activation_link(user, token),
        'logo_cid': LOGO_CID,
    }


def _password_reset_context(user, token):
    """Build the template context of the password reset email."""
    return {
        'password_reset_link': build_password_reset_link(user, token),
        'logo_cid': LOGO_CID,
    }


def send_activation_email(user, token):
    """Send the registration email carrying the account activation link."""
    context = _email_context(user, token)
    _send_email(
        subject='Confirm your email',
        to=user.email,
        html_template='accounts/activation_email.html',
        text_template='accounts/activation_email.txt',
        context=context,
    )


def send_password_reset_email(user, token):
    """Send the email carrying the password reset link."""
    context = _password_reset_context(user, token)
    _send_email(
        subject='Reset your password',
        to=user.email,
        html_template='accounts/password_reset_email.html',
        text_template='accounts/password_reset_email.txt',
        context=context,
    )


def _send_email(subject, to, html_template, text_template, context):
    """Render both bodies and send them as one multipart/related message."""
    email = EmailMultiAlternatives(
        subject=subject,
        body=render_to_string(text_template, context),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to],
    )
    email.attach_alternative(render_to_string(html_template, context), 'text/html')
    # 'related' marks the logo as belonging to the HTML body, not as a download.
    email.mixed_subtype = 'related'
    email.attach(_inline_logo())
    email.send()
