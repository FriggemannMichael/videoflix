import io
from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from PIL import Image
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.cookies import ACCESS_TOKEN_COOKIE_NAME
from videos.models import Video

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def active_user():
    return get_user_model().objects.create_user(
        username='user@example.com',
        email='user@example.com',
        password='Str0ng-test-pass!',
        is_active=True,
    )


@pytest.fixture
def authenticated_client(api_client, active_user):
    access_token = RefreshToken.for_user(active_user).access_token
    api_client.cookies[ACCESS_TOKEN_COOKIE_NAME] = str(access_token)
    return api_client


def _thumbnail_file():
    buffer = io.BytesIO()
    Image.new('RGB', (10, 10), color='blue').save(buffer, 'JPEG')
    buffer.seek(0)
    return SimpleUploadedFile('thumb.jpg', buffer.read(), content_type='image/jpeg')


def _create_video(**overrides):
    defaults = {
        'title': 'Movie',
        'description': 'A movie.',
        'category': 'Drama',
        'original_file': 'videos/original/movie.mp4',
        'processing_status': Video.ProcessingStatus.COMPLETED,
    }
    defaults.update(overrides)
    return Video.objects.create(**defaults)


def test_unauthenticated_request_returns_401(api_client):
    response = api_client.get(reverse('video_list'))

    assert response.status_code == 401


def test_request_with_invalid_token_cookie_returns_401(api_client):
    api_client.cookies[ACCESS_TOKEN_COOKIE_NAME] = 'not-a-real-token'

    response = api_client.get(reverse('video_list'))

    assert response.status_code == 401


def test_authenticated_user_can_list_completed_videos(authenticated_client):
    _create_video(title='Ready Movie')

    response = authenticated_client.get(reverse('video_list'))

    assert response.status_code == 200
    assert [video['title'] for video in response.json()] == ['Ready Movie']


def test_unfinished_videos_are_excluded(authenticated_client):
    _create_video(title='Pending', processing_status=Video.ProcessingStatus.PENDING)
    _create_video(
        title='Processing', processing_status=Video.ProcessingStatus.PROCESSING
    )
    _create_video(title='Failed', processing_status=Video.ProcessingStatus.FAILED)
    _create_video(title='Done', processing_status=Video.ProcessingStatus.COMPLETED)

    response = authenticated_client.get(reverse('video_list'))

    assert [video['title'] for video in response.json()] == ['Done']


def test_videos_are_ordered_by_created_at_descending(authenticated_client):
    older = _create_video(title='Older')
    _create_video(title='Newer')
    Video.objects.filter(pk=older.pk).update(
        created_at=timezone.now() - timedelta(days=1)
    )

    response = authenticated_client.get(reverse('video_list'))

    assert [video['title'] for video in response.json()] == ['Newer', 'Older']


def test_response_includes_expected_fields(authenticated_client):
    _create_video()

    response = authenticated_client.get(reverse('video_list'))

    assert set(response.json()[0].keys()) == {
        'id',
        'created_at',
        'title',
        'description',
        'thumbnail_url',
        'category',
    }


def test_thumbnail_url_is_none_when_missing(authenticated_client):
    _create_video()

    response = authenticated_client.get(reverse('video_list'))

    assert response.json()[0]['thumbnail_url'] is None


def test_thumbnail_url_is_absolute_when_present(
    authenticated_client, settings, tmp_path
):
    settings.MEDIA_ROOT = tmp_path
    _create_video(thumbnail=_thumbnail_file())

    response = authenticated_client.get(reverse('video_list'))

    thumbnail_url = response.json()[0]['thumbnail_url']
    assert thumbnail_url.startswith('http://testserver/media/videos/thumbnails/')
