"""Admin registration for the custom user model.

The model only adds fields to ``AbstractUser``, so Django's own ``UserAdmin``
already renders it correctly and no custom admin class is needed.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import User

admin.site.register(User, UserAdmin)
