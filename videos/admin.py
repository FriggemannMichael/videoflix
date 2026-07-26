from django.contrib import admin

from videos.models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Admin configuration for uploading and managing videos."""

    list_display = ('title', 'category', 'processing_status', 'created_at')
    list_filter = ('category', 'processing_status')
    # The conversion pipeline owns these fields, so they must not be editable.
    readonly_fields = ('processing_status', 'processing_error')
