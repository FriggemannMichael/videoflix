import io

import pytest
from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from PIL import Image

from videos.models import Video

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def _media_root(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path


def _original_file():
    return SimpleUploadedFile(
        'movie.mp4', b'fake-video-bytes', content_type='video/mp4'
    )


def _thumbnail_file():
    buffer = io.BytesIO()
    Image.new('RGB', (10, 10), color='red').save(buffer, 'JPEG')
    buffer.seek(0)
    return SimpleUploadedFile('thumb.jpg', buffer.read(), content_type='image/jpeg')


def _create_video(**overrides):
    defaults = {
        'title': 'Test Movie',
        'description': 'A movie for testing.',
        'category': 'Drama',
        'original_file': _original_file(),
    }
    defaults.update(overrides)
    return Video.objects.create(**defaults)


def test_videos_app_is_registered():
    assert apps.is_installed('videos')


def test_video_can_be_created_with_required_fields():
    video = _create_video()

    assert video.pk is not None
    assert video.title == 'Test Movie'
    assert video.category == 'Drama'
    assert video.original_file.name.endswith('movie.mp4')


def test_video_thumbnail_is_optional():
    video = _create_video()

    assert not video.thumbnail


def test_video_thumbnail_can_be_uploaded():
    video = _create_video(thumbnail=_thumbnail_file())

    assert video.thumbnail.name.endswith('thumb.jpg')


def test_video_processing_status_defaults_to_pending():
    video = _create_video()

    assert video.processing_status == Video.ProcessingStatus.PENDING


def test_video_processing_error_defaults_to_empty():
    video = _create_video()

    assert video.processing_error == ''


def test_video_created_at_and_updated_at_are_set():
    video = _create_video()

    assert video.created_at is not None
    assert video.updated_at is not None


def test_video_str_returns_title():
    video = _create_video(title='Unique Title')

    assert str(video) == 'Unique Title'


def test_video_is_registered_in_admin():
    from django.contrib import admin

    assert admin.site.is_registered(Video)


def test_video_can_be_uploaded_through_admin():
    get_user_model().objects.create_superuser(
        username='admin', email='admin@example.com', password='adminpassword'
    )
    client = Client()
    client.login(username='admin', password='adminpassword')

    response = client.post(
        '/admin/videos/video/add/',
        {
            'title': 'Admin Upload',
            'description': 'Uploaded via admin.',
            'category': 'Comedy',
            'original_file': _original_file(),
            'thumbnail': _thumbnail_file(),
        },
    )

    assert response.status_code == 302
    assert Video.objects.filter(title='Admin Upload').exists()
