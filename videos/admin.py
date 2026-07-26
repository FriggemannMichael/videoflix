from django.contrib import admin

from videos.models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Admin configuration for uploading and managing videos."""

    list_display = ('title', 'category', 'processing_status', 'created_at')
    list_filter = ('category', 'processing_status')
