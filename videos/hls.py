"""Layout of the HLS files on disk.

Single source of truth for where the conversion writes its output and where
the delivery views read it from, so both sides cannot drift apart.
"""

import re
from pathlib import Path

from django.conf import settings

RESOLUTIONS = ('480p', '720p', '1080p')
PLAYLIST_NAME = 'index.m3u8'
SEGMENT_PATTERN = re.compile(r'^[0-9]+\.ts$')


def hls_directory(video_id, resolution):
    """Return the directory that stores the HLS files for a resolution."""
    return Path(settings.MEDIA_ROOT) / 'videos' / 'hls' / str(video_id) / resolution


def playlist_path(video_id, resolution):
    """Return the filesystem path of the HLS playlist for a resolution."""
    return hls_directory(video_id, resolution) / PLAYLIST_NAME


def segment_path(video_id, resolution, segment):
    """Return the filesystem path of a single HLS segment."""
    return hls_directory(video_id, resolution) / segment
