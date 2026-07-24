from unittest.mock import MagicMock

import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def clear_cache():
    """Keep the shared Redis cache from leaking state between tests."""
    cache.clear()
    yield
    cache.clear()


@pytest.fixture(autouse=True)
def mock_rq_queue(monkeypatch):
    """Replace the RQ queue so tests never touch a real Redis queue backend."""
    queue = MagicMock()
    monkeypatch.setattr('django_rq.get_queue', lambda *args, **kwargs: queue)
    return queue
