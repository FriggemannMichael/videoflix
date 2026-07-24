from pathlib import Path

from django.conf import settings

RESOLUTIONS = ('480p', '720p', '1080p')
PLAYLIST_NAME = 'index.m3u8'


def hls_directory(video_id, resolution):
    """Return the directory that stores the HLS files for a resolution."""
    return Path(settings.MEDIA_ROOT) / 'videos' / 'hls' / str(video_id) / resolution


def playlist_path(video_id, resolution):
    """Return the filesystem path of the HLS playlist for a resolution."""
    return hls_directory(video_id, resolution) / PLAYLIST_NAME
