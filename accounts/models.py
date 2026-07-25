"""Database model for platform accounts."""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user with a unique email and privacy policy consent tracking.

    Extends Django's ``AbstractUser`` because Videoflix identifies people by
    email rather than by a chosen name: registration stores the email in both
    ``username`` and ``email``, and login authenticates against it.

    Accounts are created inactive and only ``is_active`` users can log in, so
    an account stays unusable until the activation link from the registration
    email has been opened.

    Attributes:
        email: The address used to log in; unique across all accounts.
        privacy_policy_accepted_at: When consent was given, or ``None`` if the
            registration did not include it.
    """

    email = models.EmailField(unique=True)
    privacy_policy_accepted_at = models.DateTimeField(null=True, blank=True)
