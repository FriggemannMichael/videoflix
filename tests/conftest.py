import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def clear_cache():
    """Keep the shared Redis cache from leaking state between tests."""
    cache.clear()
    yield
    cache.clear()
