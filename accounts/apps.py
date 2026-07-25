"""App configuration for accounts."""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Registers the app that owns the user model and the auth endpoints."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
