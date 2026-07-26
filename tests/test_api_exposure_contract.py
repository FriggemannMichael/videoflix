"""Guard which API endpoints require a login and which stay public.

Two regressions are cheap to introduce and expensive to find. A protected
endpoint can quietly lose its login requirement, and a public endpoint can
quietly start demanding one -- the second is what a leftover browser cookie
caused once authentication moved into a cookie, because a cookie is attached to
every request whether the endpoint needs it or not.

Both directions are checked against the live URLconf, so an endpoint added
later fails this module until its exposure is declared here on purpose.
"""

from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.urls import URLResolver, get_resolver, reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from accounts.cookies import ACCESS_TOKEN_COOKIE_NAME

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


PUBLIC = frozenset({'AllowAny'})
PROTECTED = frozenset({'IsAuthenticated'})

EXPECTED_EXPOSURE = {
    'register': PUBLIC,
    'activate': PUBLIC,
    'login': PUBLIC,
    'logout': PUBLIC,
    'token_refresh': PUBLIC,
    'password_reset': PUBLIC,
    'password_confirm': PUBLIC,
    'video_list': PROTECTED,
    'video_playlist': PROTECTED,
    'video_segment': PROTECTED,
}

# A link that is well-formed but matches nothing, so the view runs its own
# checks instead of failing on the URL pattern.
DEAD_LINK = ('MQ', 'not-a-real-token')
PASSWORD = 'Str0ng-test-pass!'

# One request per endpoint that reaches the view. The bodies do not have to
# succeed: these tests only ask whether the request was let through at all.
PUBLIC_REQUESTS = {
    'register': {
        'method': 'post',
        'data': {
            'email': 'contract@example.com',
            'password': PASSWORD,
            'confirmed_password': PASSWORD,
        },
    },
    'activate': {'method': 'get', 'args': DEAD_LINK},
    'login': {
        'method': 'post',
        'data': {'email': 'contract@example.com', 'password': PASSWORD},
    },
    'logout': {'method': 'post'},
    'token_refresh': {'method': 'post'},
    'password_reset': {
        'method': 'post',
        'data': {'email': 'contract@example.com'},
    },
    'password_confirm': {
        'method': 'post',
        'args': DEAD_LINK,
        'data': {'new_password': PASSWORD, 'confirm_password': PASSWORD},
    },
}

PROTECTED_REQUESTS = {
    'video_list': {'method': 'get'},
    'video_playlist': {'method': 'get', 'args': (1, '480p')},
    'video_segment': {'method': 'get', 'args': (1, '480p', '000.ts')},
}

UNUSABLE_COOKIES = ('garbage', 'expired', 'deleted user')


def api_exposure():
    """Map every DRF endpoint in the project to its permission class names."""
    return {
        pattern.name: frozenset(
            permission.__name__
            for permission in pattern.callback.cls.permission_classes
        )
        for pattern in url_patterns(get_resolver().url_patterns)
        if hasattr(pattern.callback, 'cls')
    }


def url_patterns(patterns):
    """Yield every leaf URL pattern, descending into included URLconfs."""
    for entry in patterns:
        if isinstance(entry, URLResolver):
            yield from url_patterns(entry.url_patterns)
        else:
            yield entry


def unusable_cookie(case):
    """Return an access token a browser could still be holding on to."""
    if case == 'garbage':
        return 'not-a-jwt'
    user = get_user_model().objects.create_user(
        username='stale@example.com', email='stale@example.com', password=PASSWORD
    )
    if case == 'expired':
        token = AccessToken.for_user(user)
        token.set_exp(lifetime=timedelta(seconds=-1))
        return str(token)
    token = str(AccessToken.for_user(user))
    user.delete()
    return token


def send(client, name, recipe):
    """Send the recipe's request to the named endpoint."""
    url = reverse(name, args=recipe.get('args', ()))
    method = getattr(client, recipe['method'])
    if 'data' in recipe:
        return method(url, recipe['data'], format='json')
    return method(url)


def test_api_exposure_matches_the_declared_contract():
    """Fail on any endpoint that is added, removed, or changes its permissions."""
    assert api_exposure() == EXPECTED_EXPOSURE


def test_every_endpoint_in_the_contract_has_a_request_recipe():
    """Keep the checks below from silently skipping a new endpoint."""
    declared = set(PUBLIC_REQUESTS) | set(PROTECTED_REQUESTS)
    assert declared == set(EXPECTED_EXPOSURE)


@pytest.mark.parametrize('name', sorted(PUBLIC_REQUESTS))
@pytest.mark.parametrize('case', UNUSABLE_COOKIES)
def test_public_endpoint_is_not_blocked_by_an_unusable_cookie(api_client, name, case):
    api_client.cookies[ACCESS_TOKEN_COOKIE_NAME] = unusable_cookie(case)

    response = send(api_client, name, PUBLIC_REQUESTS[name])

    assert response.status_code not in (
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    )


@pytest.mark.parametrize('name', sorted(PUBLIC_REQUESTS))
def test_public_endpoint_is_not_blocked_without_any_cookie(api_client, name):
    response = send(api_client, name, PUBLIC_REQUESTS[name])

    assert response.status_code not in (
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    )


@pytest.mark.parametrize('name', sorted(PROTECTED_REQUESTS))
def test_protected_endpoint_rejects_an_anonymous_request(api_client, name):
    response = send(api_client, name, PROTECTED_REQUESTS[name])

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize('name', sorted(PROTECTED_REQUESTS))
@pytest.mark.parametrize('case', UNUSABLE_COOKIES)
def test_protected_endpoint_rejects_an_unusable_cookie(api_client, name, case):
    api_client.cookies[ACCESS_TOKEN_COOKIE_NAME] = unusable_cookie(case)

    response = send(api_client, name, PROTECTED_REQUESTS[name])

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
