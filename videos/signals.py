from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from videos.cache import invalidate_video_list_cache
from videos.models import Video


@receiver(post_save, sender=Video)
@receiver(post_delete, sender=Video)
def clear_video_list_cache(sender, instance, **kwargs):
    """Invalidate the cached video list whenever a video changes."""
    invalidate_video_list_cache()
