"""Admin registration for accounts.

The custom user model only adds fields to Django's ``AbstractUser``, so
Django's own ``UserAdmin`` is registered unchanged.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import User

admin.site.register(User, UserAdmin)
