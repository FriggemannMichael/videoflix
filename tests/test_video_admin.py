"""The processing state is owned by the pipeline, not by admin users."""

import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from videos.admin import UPLOAD_FIELDS, VideoAdmin, VideoAdminForm
from videos.models import Video

pytestmark = pytest.mark.django_db

PIPELINE_FIELDS = ('processing_status', 'processing_error')


def _upload_payload(**overrides):
    payload = {
        'title': 'Uploaded via admin',
        'description': 'a description',
        'category': 'Drama',
        'original_file': SimpleUploadedFile(
            'movie.mp4', b'not-a-real-movie', content_type='video/mp4'
        ),
    }
    payload.update(overrides)
    return {key: value for key, value in payload.items() if value is not None}


@pytest.fixture
def admin_user():
    return get_user_model().objects.create_superuser(
        username='admin@example.com',
        email='admin@example.com',
        password='Str0ng-test-pass!',
    )


@pytest.fixture
def admin_client(client, admin_user):
    client.force_login(admin_user)
    return client


@pytest.mark.parametrize('field', PIPELINE_FIELDS)
def test_pipeline_fields_are_read_only(field):
    admin = VideoAdmin(Video, AdminSite())

    assert field in admin.get_readonly_fields(request=None)


@pytest.mark.parametrize('field', PIPELINE_FIELDS)
def test_add_form_has_no_input_for_pipeline_fields(admin_client, field):
    response = admin_client.get(reverse('admin:videos_video_add'))

    assert f'name="{field}"' not in response.content.decode()


def test_uploading_starts_as_pending_even_if_a_status_is_posted(admin_client):
    response = admin_client.post(
        reverse('admin:videos_video_add'),
        _upload_payload(
            processing_status=Video.ProcessingStatus.COMPLETED,
            processing_error='injected',
        ),
    )

    assert response.status_code == 302
    video = Video.objects.get(title='Uploaded via admin')
    assert video.processing_status == Video.ProcessingStatus.PENDING
    assert video.processing_error == ''


@pytest.mark.parametrize('field', UPLOAD_FIELDS)
def test_upload_fields_are_required(field):
    assert VideoAdminForm().fields[field].required is True


@pytest.mark.parametrize('field', UPLOAD_FIELDS)
def test_add_form_marks_the_upload_fields_as_required(admin_client, field):
    response = admin_client.get(reverse('admin:videos_video_add'))

    assert f'class="required" for="id_{field}"' in response.content.decode()


@pytest.mark.parametrize('field', UPLOAD_FIELDS)
def test_upload_without_a_required_field_is_rejected(admin_client, field):
    response = admin_client.post(
        reverse('admin:videos_video_add'), _upload_payload(**{field: None})
    )

    assert response.status_code == 200
    assert 'This field is required.' in response.content.decode()
    assert not Video.objects.exists()


def test_thumbnail_stays_optional_because_the_pipeline_creates_it(admin_client):
    response = admin_client.post(reverse('admin:videos_video_add'), _upload_payload())

    assert response.status_code == 302
    assert not Video.objects.get(title='Uploaded via admin').thumbnail
