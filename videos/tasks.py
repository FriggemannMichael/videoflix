import subprocess
import tempfile
from pathlib import Path

from django.conf import settings
from django.core.files import File

from videos.hls import RESOLUTIONS, hls_directory
from videos.models import Video

__all__ = ['RESOLUTIONS', 'convert_to_hls', 'generate_thumbnail']

THUMBNAIL_TIMESTAMP = '00:00:01'

RESOLUTION_HEIGHTS = {'480p': 480, '720p': 720, '1080p': 1080}
HLS_ENCODE_ARGS = [
    '-c:v',
    'h264',
    '-c:a',
    'aac',
    '-f',
    'hls',
    '-hls_time',
    '4',
    '-hls_playlist_type',
    'vod',
]


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


def convert_to_hls(video_id):
    """Convert a video to HLS at every resolution (RQ background task)."""
    video = Video.objects.get(pk=video_id)
    _mark_processing(video)
    try:
        for resolution in RESOLUTIONS:
            _convert_resolution(video, resolution)
        _mark_completed(video)
    except Exception as exc:
        _record_failure(video, exc)
        raise


def _convert_resolution(video, resolution):
    """Produce the HLS playlist and segments for a single resolution."""
    output_dir = hls_directory(video.pk, resolution)
    output_dir.mkdir(parents=True, exist_ok=True)
    playlist = output_dir / 'index.m3u8'
    subprocess.run(
        _hls_command(video.original_file.path, resolution, output_dir, playlist),
        check=True,
        capture_output=True,
    )
    _verify_output(output_dir, playlist)


def _hls_command(source, resolution, output_dir, playlist):
    """Build the FFmpeg HLS argument list (no shell, safe from injection)."""
    ffmpeg_path = getattr(settings, 'FFMPEG_PATH', 'ffmpeg')
    scale = f'scale=-2:{RESOLUTION_HEIGHTS[resolution]}'
    inputs = [ffmpeg_path, '-y', '-i', source, '-vf', scale]
    outputs = ['-hls_segment_filename', str(output_dir / '%03d.ts'), str(playlist)]
    return inputs + HLS_ENCODE_ARGS + outputs


def _verify_output(output_dir, playlist):
    """Ensure FFmpeg actually produced a playlist and at least one segment."""
    if not playlist.exists():
        raise RuntimeError(f'HLS playlist missing: {playlist}')
    if not any(output_dir.glob('*.ts')):
        raise RuntimeError(f'HLS segments missing in: {output_dir}')


def _mark_processing(video):
    """Mark the video as currently being processed."""
    video.processing_status = Video.ProcessingStatus.PROCESSING
    video.save(update_fields=['processing_status', 'updated_at'])


def _mark_completed(video):
    """Mark the video as successfully processed and ready to stream."""
    video.processing_status = Video.ProcessingStatus.COMPLETED
    video.processing_error = ''
    video.save(update_fields=['processing_status', 'processing_error', 'updated_at'])


def _record_failure(video, exc):
    """Mark the video as failed and persist the error message."""
    video.processing_status = Video.ProcessingStatus.FAILED
    video.processing_error = str(exc)
    video.save(update_fields=['processing_status', 'processing_error', 'updated_at'])
