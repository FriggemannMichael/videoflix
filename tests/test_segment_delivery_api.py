from pathlib import Path

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.cookies import ACCESS_TOKEN_COOKIE_NAME
from videos.models import Video

pytestmark = pytest.mark.django_db

SEGMENT_NAME = '000.ts'
SEGMENT_BODY = b'\x47segment-bytes'


@pytest.fixture(autouse=True)
def _media_root(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def active_user():
    return get_user_model().objects.create_user(
        username='viewer@example.com',
        email='viewer@example.com',
        password='Str0ng-test-pass!',
        is_active=True,
    )


@pytest.fixture
def authenticated_client(api_client, active_user):
    access_token = RefreshToken.for_user(active_user).access_token
    api_client.cookies[ACCESS_TOKEN_COOKIE_NAME] = str(access_token)
    return api_client


def _create_video(status=Video.ProcessingStatus.COMPLETED):
    return Video.objects.create(
        title='Ready Movie',
        description='A processed movie.',
        category='Drama',
        processing_status=status,
    )


def _write_segment(video, resolution, name=SEGMENT_NAME, content=SEGMENT_BODY):
    directory = (
        Path(settings.MEDIA_ROOT) / 'videos' / 'hls' / str(video.id) / resolution
    )
    directory.mkdir(parents=True, exist_ok=True)
    (directory / name).write_bytes(content)


def _url(movie_id, resolution, segment):
    return reverse(
        'video_segment',
        kwargs={'movie_id': movie_id, 'resolution': resolution, 'segment': segment},
    )


def test_authenticated_user_receives_segment(authenticated_client):
    video = _create_video()
    _write_segment(video, '480p')

    response = authenticated_client.get(_url(video.id, '480p', SEGMENT_NAME))

    assert response.status_code == 200
    assert response['Content-Type'] == 'video/mp2t'
    body = b''.join(response.streaming_content)
    assert body == SEGMENT_BODY


def test_segment_url_has_no_trailing_slash():
    # hls.js requests segments relative to the manifest without a trailing
    # slash; the route must match that directly, with no APPEND_SLASH redirect.
    assert not _url(1, '480p', SEGMENT_NAME).endswith('/')


def test_unauthenticated_request_is_rejected(api_client):
    video = _create_video()
    _write_segment(video, '480p')

    response = api_client.get(_url(video.id, '480p', SEGMENT_NAME))

    assert response.status_code == 401


def test_unknown_movie_id_returns_404(authenticated_client):
    response = authenticated_client.get(_url(999, '480p', SEGMENT_NAME))

    assert response.status_code == 404


def test_video_not_yet_ready_returns_404(authenticated_client):
    video = _create_video(status=Video.ProcessingStatus.PROCESSING)
    _write_segment(video, '480p')

    response = authenticated_client.get(_url(video.id, '480p', SEGMENT_NAME))

    assert response.status_code == 404


def test_invalid_resolution_returns_404(authenticated_client):
    video = _create_video()
    _write_segment(video, '480p')

    response = authenticated_client.get(_url(video.id, '999p', SEGMENT_NAME))

    assert response.status_code == 404


def test_missing_segment_file_returns_404(authenticated_client):
    video = _create_video()

    response = authenticated_client.get(_url(video.id, '720p', SEGMENT_NAME))

    assert response.status_code == 404


@pytest.mark.parametrize('segment', ['000.mp4', 'segment', 'abc.ts', '00a.ts'])
def test_invalid_segment_name_returns_404(authenticated_client, segment):
    video = _create_video()
    _write_segment(video, '480p')

    response = authenticated_client.get(_url(video.id, '480p', segment))

    assert response.status_code == 404
