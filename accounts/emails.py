"""Composing and sending the transactional account emails.

Both the activation and the password reset mail are sent as multipart
messages: a plain text body plus an HTML alternative rendered from the
templates in ``accounts/templates/accounts/``. The links they contain point
into the frontend, not the API, because the user finishes the flow there.
"""

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


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


def _logo_url(request):
    """Return an absolute URL for the logo, as email clients need one."""
    return request.build_absolute_uri(static('accounts/img/logo.png'))


def _email_context(request, user, token):
    """Build the template context of the activation email."""
    return {
        'activation_link': build_activation_link(user, token),
        'logo_url': _logo_url(request),
    }


def _password_reset_context(request, user, token):
    """Build the template context of the password reset email."""
    return {
        'password_reset_link': build_password_reset_link(user, token),
        'logo_url': _logo_url(request),
    }


def send_activation_email(request, user, token):
    """Send the registration email carrying the account activation link."""
    context = _email_context(request, user, token)
    _send_email(
        subject='Confirm your email',
        to=user.email,
        html_template='accounts/activation_email.html',
        text_template='accounts/activation_email.txt',
        context=context,
    )


def send_password_reset_email(request, user, token):
    """Send the email carrying the password reset link."""
    context = _password_reset_context(request, user, token)
    _send_email(
        subject='Reset your password',
        to=user.email,
        html_template='accounts/password_reset_email.html',
        text_template='accounts/password_reset_email.txt',
        context=context,
    )


def _send_email(subject, to, html_template, text_template, context):
    """Render both bodies and send them as one multipart message."""
    html_body = render_to_string(html_template, context)
    text_body = render_to_string(text_template, context)
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to],
    )
    email.attach_alternative(html_body, 'text/html')
    email.send()
