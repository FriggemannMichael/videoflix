import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from videos.models import Video
from videos.tasks import convert_to_hls

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


def test_creating_video_enqueues_hls_conversion_task(mock_rq_queue):
    video = _create_video()

    mock_rq_queue.enqueue.assert_any_call(convert_to_hls, video.id)


def test_updating_video_does_not_enqueue_hls_conversion_task(mock_rq_queue):
    video = _create_video()
    mock_rq_queue.enqueue.reset_mock()

    video.title = 'Renamed'
    video.save()

    mock_rq_queue.enqueue.assert_not_called()
