"""Helpers shared by the account views.

Kept out of ``views.py`` so that module contains only views returning a
response.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from accounts.emails import send_password_reset_email


def get_user_from_uidb64(uidb64):
    """Resolve the user encoded in a uidb64 URL parameter, or None if invalid."""
    user_model = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        return user_model.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, user_model.DoesNotExist):
        return None


def send_reset_email_if_user_exists(email):
    """Send a password reset email if the address belongs to a user."""
    user = get_user_model().objects.filter(email__iexact=email).first()
    if user is not None:
        token = default_token_generator.make_token(user)
        send_password_reset_email(user, token)
