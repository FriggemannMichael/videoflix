from django.apps import apps
from django.conf import settings
from django.urls import reverse


def test_django_rq_is_registered():
    assert apps.is_installed('django_rq')


def test_admin_url_is_registered():
    assert reverse('admin:index') == '/admin/'


def test_database_uses_postgresql():
    assert settings.DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql'


def test_cache_uses_redis():
    assert settings.CACHES['default']['BACKEND'] == 'django_redis.cache.RedisCache'


def test_rq_default_queue_is_configured():
    assert 'default' in settings.RQ_QUEUES


def test_static_and_media_paths_are_configured():
    assert settings.STATIC_URL == '/static/'
    assert settings.MEDIA_URL == '/media/'
    assert settings.STATIC_ROOT == settings.BASE_DIR / 'static'
    assert settings.MEDIA_ROOT == settings.BASE_DIR / 'media'
