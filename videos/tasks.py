import subprocess
import tempfile
from pathlib import Path

from django.conf import settings
from django.core.files import File

from videos.models import Video

THUMBNAIL_TIMESTAMP = '00:00:01'


def generate_thumbnail(video_id):
    """Extract a single frame from a video as its thumbnail (RQ background task).

    On failure the video is marked as failed and the error is stored in
    ``processing_error`` before the exception is re-raised so the RQ worker
    records the job as failed.
    """
    video = Video.objects.get(pk=video_id)
    try:
        _create_thumbnail(video)
    except Exception as exc:
        _record_failure(video, exc)
        raise


def _create_thumbnail(video):
    """Run FFmpeg to grab a frame and store it on the video's thumbnail field."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_path = Path(tmp_dir) / f'{video.pk}.jpg'
        subprocess.run(
            _ffmpeg_command(video.original_file.path, str(output_path)),
            check=True,
            capture_output=True,
        )
        with output_path.open('rb') as thumbnail:
            video.thumbnail.save(f'{video.pk}.jpg', File(thumbnail), save=True)


def _ffmpeg_command(source, destination):
    """Build the FFmpeg argument list (no shell, safe from injection)."""
    ffmpeg_path = getattr(settings, 'FFMPEG_PATH', 'ffmpeg')
    return [
        ffmpeg_path,
        '-y',
        '-ss',
        THUMBNAIL_TIMESTAMP,
        '-i',
        source,
        '-frames:v',
        '1',
        destination,
    ]


def _record_failure(video, exc):
    """Mark the video as failed and persist the error message."""
    video.processing_status = Video.ProcessingStatus.FAILED
    video.processing_error = str(exc)
    video.save(update_fields=['processing_status', 'processing_error', 'updated_at'])
