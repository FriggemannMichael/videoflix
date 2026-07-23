from django.core.cache import cache

VIDEO_LIST_CACHE_KEY = 'video_list'
VIDEO_LIST_CACHE_TIMEOUT = 300


def get_cached_video_list():
    """Return the cached video list payload, or None when it is not cached."""
    return cache.get(VIDEO_LIST_CACHE_KEY)


def set_cached_video_list(data):
    """Cache the video list payload for a short time."""
    cache.set(VIDEO_LIST_CACHE_KEY, data, VIDEO_LIST_CACHE_TIMEOUT)


def invalidate_video_list_cache():
    """Drop the cached video list so the next request rebuilds it."""
    cache.delete(VIDEO_LIST_CACHE_KEY)
