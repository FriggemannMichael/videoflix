import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.cookies import ACCESS_TOKEN_COOKIE_NAME
from videos.cache import VIDEO_LIST_CACHE_KEY, VIDEO_LIST_CACHE_TIMEOUT
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


def _create_video_without_signals(title):
    """Insert a video without firing post_save, so the cache stays untouched."""
    Video.objects.bulk_create(
        [
            Video(
                title=title,
                description='A movie.',
                category='Drama',
                original_file='videos/original/movie.mp4',
                processing_status=Video.ProcessingStatus.COMPLETED,
            )
        ]
    )


def _titles(response):
    return [video['title'] for video in response.json()]


def test_first_request_fills_the_cache(authenticated_client):
    _create_video(title='Ready Movie')

    authenticated_client.get(reverse('video_list'))

    assert cache.get(VIDEO_LIST_CACHE_KEY) is not None


def test_repeated_request_is_served_from_the_cache(authenticated_client):
    _create_video(title='Cached Movie')
    authenticated_client.get(reverse('video_list'))
    _create_video_without_signals('Invisible Movie')

    response = authenticated_client.get(reverse('video_list'))

    assert _titles(response) == ['Cached Movie']


def test_cached_video_list_expires_after_a_short_time(authenticated_client):
    _create_video()

    authenticated_client.get(reverse('video_list'))

    assert VIDEO_LIST_CACHE_TIMEOUT <= 300
    assert 0 < cache.ttl(VIDEO_LIST_CACHE_KEY) <= VIDEO_LIST_CACHE_TIMEOUT


def test_creating_a_video_invalidates_the_cache(authenticated_client):
    _create_video(title='First Movie')
    authenticated_client.get(reverse('video_list'))

    _create_video(title='Second Movie')

    assert cache.get(VIDEO_LIST_CACHE_KEY) is None
    response = authenticated_client.get(reverse('video_list'))
    assert set(_titles(response)) == {'First Movie', 'Second Movie'}


def test_updating_a_video_invalidates_the_cache(authenticated_client):
    video = _create_video(title='Old Title')
    authenticated_client.get(reverse('video_list'))

    video.title = 'New Title'
    video.save()

    assert cache.get(VIDEO_LIST_CACHE_KEY) is None
    response = authenticated_client.get(reverse('video_list'))
    assert _titles(response) == ['New Title']


def test_deleting_a_video_invalidates_the_cache(authenticated_client):
    video = _create_video(title='Doomed Movie')
    authenticated_client.get(reverse('video_list'))

    video.delete()

    assert cache.get(VIDEO_LIST_CACHE_KEY) is None
    response = authenticated_client.get(reverse('video_list'))
    assert _titles(response) == []


def test_finished_processing_invalidates_the_cache(authenticated_client):
    video = _create_video(
        title='Pending Movie', processing_status=Video.ProcessingStatus.PENDING
    )
    authenticated_client.get(reverse('video_list'))

    video.processing_status = Video.ProcessingStatus.COMPLETED
    video.save()

    response = authenticated_client.get(reverse('video_list'))
    assert _titles(response) == ['Pending Movie']


def test_cached_list_is_not_served_to_unauthenticated_clients(authenticated_client):
    _create_video(title='Secret Movie')
    authenticated_client.get(reverse('video_list'))

    response = APIClient().get(reverse('video_list'))

    assert response.status_code == 401
