import pytest

from videos.models import Video
from videos.serializers import VideoListSerializer

pytestmark = pytest.mark.django_db


def _video(**overrides):
    defaults = {
        'title': 'Movie',
        'description': 'A movie.',
        'category': 'Drama',
        'original_file': 'videos/original/movie.mp4',
        'thumbnail': 'videos/thumbnails/thumb.jpg',
        'processing_status': Video.ProcessingStatus.COMPLETED,
    }
    defaults.update(overrides)
    return Video.objects.create(**defaults)


def test_thumbnail_url_is_relative_without_request_context():
    # Without a request in the serializer context the URL cannot be made
    # absolute, so the relative media path is returned as-is.
    video = _video()

    data = VideoListSerializer(video).data

    assert data['thumbnail_url'] == video.thumbnail.url
    assert data['thumbnail_url'].startswith('/')


def test_thumbnail_url_is_none_without_thumbnail():
    video = _video(thumbnail='')

    data = VideoListSerializer(video).data

    assert data['thumbnail_url'] is None
