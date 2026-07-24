import subprocess
from pathlib import Path

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from videos.models import Video
from videos.tasks import generate_thumbnail

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def _media_root(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path


def _create_video(**overrides):
    defaults = {
        'title': 'Test Movie',
        'description': 'A movie for testing.',
        'category': 'Drama',
        'original_file': SimpleUploadedFile(
            'movie.mp4', b'fake-video-bytes', content_type='video/mp4'
        ),
    }
    defaults.update(overrides)
    return Video.objects.create(**defaults)


def _write_frame(command, *args, **kwargs):
    """Stand in for FFmpeg by writing a real JPEG to the output path."""
    output_path = Path(command[-1])
    Image.new('RGB', (10, 10), color='blue').save(output_path, 'JPEG')
    return subprocess.CompletedProcess(command, 0)


def test_generate_thumbnail_saves_a_thumbnail(monkeypatch):
    video = _create_video()
    monkeypatch.setattr('videos.tasks.subprocess.run', _write_frame)

    generate_thumbnail(video.id)

    video.refresh_from_db()
    assert video.thumbnail
    assert video.processing_error == ''
    assert video.processing_status != Video.ProcessingStatus.FAILED


def test_generate_thumbnail_uses_a_safe_subprocess_call(monkeypatch):
    video = _create_video()
    calls = {}

    def _capture(command, *args, **kwargs):
        calls['command'] = command
        calls['kwargs'] = kwargs
        return _write_frame(command, *args, **kwargs)

    monkeypatch.setattr('videos.tasks.subprocess.run', _capture)

    generate_thumbnail(video.id)

    assert isinstance(calls['command'], list)
    assert calls['kwargs'].get('shell', False) is False
    assert calls['kwargs'].get('check') is True


def test_generate_thumbnail_records_error_on_failure(monkeypatch):
    video = _create_video()

    def _fail(command, *args, **kwargs):
        raise subprocess.CalledProcessError(1, command, stderr=b'ffmpeg boom')

    monkeypatch.setattr('videos.tasks.subprocess.run', _fail)

    with pytest.raises(subprocess.CalledProcessError):
        generate_thumbnail(video.id)

    video.refresh_from_db()
    assert video.processing_status == Video.ProcessingStatus.FAILED
    assert video.processing_error != ''
    assert not video.thumbnail
