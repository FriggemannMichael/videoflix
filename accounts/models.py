from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user with a unique email and privacy policy consent tracking."""

    email = models.EmailField(unique=True)
    privacy_policy_accepted_at = models.DateTimeField(null=True, blank=True)
