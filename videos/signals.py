import django_rq
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from videos.cache import invalidate_video_list_cache
from videos.models import Video
from videos.tasks import convert_to_hls, generate_thumbnail


@receiver(post_save, sender=Video)
@receiver(post_delete, sender=Video)
def clear_video_list_cache(sender, instance, **kwargs):
    """Invalidate the cached video list whenever a video changes."""
    invalidate_video_list_cache()


@receiver(post_save, sender=Video, dispatch_uid='videos.enqueue_thumbnail')
def enqueue_thumbnail(sender, instance, created, **kwargs):
    """Queue thumbnail generation in the background for newly uploaded videos."""
    if not created:
        return
    django_rq.get_queue('default').enqueue(generate_thumbnail, instance.id)


@receiver(post_save, sender=Video, dispatch_uid='videos.enqueue_hls')
def enqueue_hls_conversion(sender, instance, created, **kwargs):
    """Queue HLS conversion in the background for newly uploaded videos."""
    if not created:
        return
    django_rq.get_queue('default').enqueue(convert_to_hls, instance.id)
