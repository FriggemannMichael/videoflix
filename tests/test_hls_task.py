import subprocess
from pathlib import Path

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from videos.models import Video
from videos.tasks import RESOLUTION_HEIGHTS, RESOLUTIONS, convert_to_hls

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


def _fake_hls(command, *args, **kwargs):
    """Stand in for FFmpeg by writing a playlist and one segment."""
    playlist = Path(command[-1])
    playlist.write_text('#EXTM3U\n')
    (playlist.parent / '000.ts').write_bytes(b'segment-bytes')
    return subprocess.CompletedProcess(command, 0)


def _hls_dir(tmp_path, video, resolution):
    return tmp_path / 'videos' / 'hls' / str(video.id) / resolution


def test_convert_to_hls_creates_playlists_and_segments(monkeypatch, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    video = _create_video()
    monkeypatch.setattr('videos.tasks.subprocess.run', _fake_hls)

    convert_to_hls(video.id)

    video.refresh_from_db()
    assert video.processing_status == Video.ProcessingStatus.COMPLETED
    assert video.processing_error == ''
    for resolution in RESOLUTIONS:
        base = _hls_dir(tmp_path, video, resolution)
        assert (base / 'index.m3u8').exists()
        assert list(base.glob('*.ts'))


def test_convert_to_hls_scales_each_resolution_to_its_height(
    monkeypatch, tmp_path, settings
):
    settings.MEDIA_ROOT = tmp_path
    video = _create_video()
    commands = []

    def _capture(command, *args, **kwargs):
        commands.append(' '.join(command))
        return _fake_hls(command, *args, **kwargs)

    monkeypatch.setattr('videos.tasks.subprocess.run', _capture)

    convert_to_hls(video.id)

    for resolution in RESOLUTIONS:
        height = RESOLUTION_HEIGHTS[resolution]
        assert any(
            f'scale=-2:{height}' in cmd and f'/{resolution}/' in cmd for cmd in commands
        )
    assert all('%03d.ts' in cmd and cmd.endswith('index.m3u8') for cmd in commands)


def test_convert_to_hls_uses_a_safe_subprocess_call(monkeypatch, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    video = _create_video()
    calls = []

    def _capture(command, *args, **kwargs):
        calls.append((command, kwargs))
        return _fake_hls(command, *args, **kwargs)

    monkeypatch.setattr('videos.tasks.subprocess.run', _capture)

    convert_to_hls(video.id)

    assert len(calls) == len(RESOLUTIONS)
    for command, kwargs in calls:
        assert isinstance(command, list)
        assert kwargs.get('shell', False) is False
        assert kwargs.get('check') is True


def test_convert_to_hls_records_error_when_ffmpeg_fails(
    monkeypatch, tmp_path, settings
):
    settings.MEDIA_ROOT = tmp_path
    video = _create_video()

    def _fail(command, *args, **kwargs):
        raise subprocess.CalledProcessError(1, command, stderr=b'ffmpeg boom')

    monkeypatch.setattr('videos.tasks.subprocess.run', _fail)

    with pytest.raises(subprocess.CalledProcessError):
        convert_to_hls(video.id)

    video.refresh_from_db()
    assert video.processing_status == Video.ProcessingStatus.FAILED
    assert video.processing_error != ''


def test_convert_to_hls_fails_when_playlist_missing(monkeypatch, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    video = _create_video()

    def _noop(command, *args, **kwargs):
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr('videos.tasks.subprocess.run', _noop)

    with pytest.raises(RuntimeError):
        convert_to_hls(video.id)

    video.refresh_from_db()
    assert video.processing_status == Video.ProcessingStatus.FAILED


def test_convert_to_hls_fails_when_segments_missing(monkeypatch, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    video = _create_video()

    def _playlist_only(command, *args, **kwargs):
        Path(command[-1]).write_text('#EXTM3U\n')
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr('videos.tasks.subprocess.run', _playlist_only)

    with pytest.raises(RuntimeError):
        convert_to_hls(video.id)

    video.refresh_from_db()
    assert video.processing_status == Video.ProcessingStatus.FAILED
