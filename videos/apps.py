"""App configuration for the video catalogue."""

from django.apps import AppConfig


class VideosConfig(AppConfig):
    """Registers the app that owns videos, the HLS pipeline, and delivery."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'videos'

    def ready(self):
        """Import the signal receivers so they are connected on startup."""
        import videos.signals  # noqa: F401
