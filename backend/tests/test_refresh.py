"""Refresh-token rotation and the absolute session lifetime (Slice 3)."""

from datetime import timedelta

import jwt
import pytest
from django.conf import settings as django_settings
from freezegun import freeze_time

from accounts import tokens
from accounts.models import RevokedRefreshToken, revoke_refresh_token
from tests.helpers import (
    REFRESH_URL,
    bootstrap_csrf,
    decode_unverified,
    login,
    refresh,
    refresh_cookie,
    set_refresh_cookie,
)
from tests.test_login import with_header_alg

pytestmark = pytest.mark.django_db

INVALID_REFRESH = {"detail": "Refresh token is invalid or expired."}
LOGIN_TIME = "2026-08-01T09:00:00+00:00"


@pytest.fixture
def user(make_user):
    return make_user(email="person@example.com")


@pytest.fixture
def logged_in(api_client, user):
    """A client holding a fresh session's refresh-token cookie."""
    response = login(api_client, user.email)
    assert response.status_code == 200
    return api_client


def assert_rejected_without_credentials(response, *, cookie_cleared=True):
    assert response.status_code == 401
    assert response.json() == INVALID_REFRESH
    assert "access_token" not in response.json()
    if cookie_cleared:
        cleared = response.cookies["refresh_token"]
        assert cleared.value == ""
        assert int(cleared["max-age"]) == 0
        assert cleared["path"] == "/api/v1/auth/"
        assert cleared["httponly"] is True
    else:
        assert not refresh_cookie(response)


def test_tc_fr_007_01_a_valid_refresh_token_returns_a_new_access_token(api_client, user):
    """TC-FR-007-01 — A valid refresh token returns a new access token."""
    with freeze_time(LOGIN_TIME) as frozen:
        first_access = login(api_client, user.email).json()["access_token"]
        frozen.tick(timedelta(minutes=5))

        response = refresh(api_client)

        assert response.status_code == 200
        new_access = response.json()["access_token"]
        assert new_access != first_access
        assert tokens.decode_access_token(new_access)["sub"] == str(user.pk)


def test_tc_fr_007_02_refresh_rotates_and_invalidates_the_previous_refresh_token(logged_in):
    """TC-FR-007-02 — Refresh rotates and invalidates the previous refresh token."""
    original = refresh_cookie(logged_in)

    first = refresh(logged_in)
    assert first.status_code == 200
    assert refresh_cookie(first) != original

    set_refresh_cookie(logged_in, original)
    second = refresh(logged_in)

    assert_rejected_without_credentials(second)


def test_tc_fr_007_03_successful_refresh_replaces_the_refresh_token_cookie(api_client, user):
    """TC-FR-007-03 — Successful refresh replaces the refresh-token cookie."""
    with freeze_time(LOGIN_TIME) as frozen:
        login(api_client, user.email)
        original = refresh_cookie(api_client)
        frozen.tick(timedelta(days=1))

        response = refresh(api_client)

    replacement = response.cookies["refresh_token"]
    assert replacement.value and replacement.value != original
    assert replacement["httponly"] is True
    assert replacement["domain"] == ""
    assert replacement["path"] == "/api/v1/auth/"
    assert not replacement["secure"]  # local development configuration
    assert replacement["samesite"] == "Lax"
    # Expiry aligned with the token: six days remain of the seven-day session.
    assert int(replacement["max-age"]) == int(timedelta(days=6).total_seconds())


def test_tc_fr_007_04_refreshed_access_token_is_returned_in_the_documented_field(logged_in):
    """TC-FR-007-04 — Refreshed access token is returned in the documented field."""
    response = refresh(logged_in)

    assert response.status_code == 200
    assert set(response.json()) == {"access_token"}
    assert tokens.decode_access_token(response.json()["access_token"])["token_type"] == "access"


def test_tc_fr_007_05_refresh_is_rejected_for_an_expired_refresh_token(api_client, user):
    """TC-FR-007-05 — Refresh is rejected for an expired refresh token."""
    with freeze_time(LOGIN_TIME) as frozen:
        login(api_client, user.email)
        frozen.tick(timedelta(days=8))

        response = refresh(api_client)

    assert_rejected_without_credentials(response)


def test_tc_fr_007_06_refresh_is_rejected_for_a_revoked_refresh_token(logged_in):
    """TC-FR-007-06 — Refresh is rejected for a revoked refresh token."""
    revoke_refresh_token(tokens.decode_refresh_token(refresh_cookie(logged_in)))

    response = refresh(logged_in)

    assert_rejected_without_credentials(response)


def test_tc_fr_007_07_refresh_is_rejected_for_a_malformed_refresh_token(api_client, user):
    """TC-FR-007-07 — Refresh is rejected for a malformed refresh token."""
    set_refresh_cookie(api_client, "not-a-jwt.at-all")

    response = refresh(api_client)

    assert_rejected_without_credentials(response)
    assert RevokedRefreshToken.objects.count() == 0


def test_tc_fr_007_08_refresh_is_rejected_for_a_missing_refresh_token(api_client, user):
    """TC-FR-007-08 — Refresh is rejected for a missing refresh token."""
    assert "refresh_token" not in api_client.cookies

    response = refresh(api_client)

    assert response.status_code == 401
    assert response.json() == INVALID_REFRESH
    assert not refresh_cookie(response)


def test_tc_fr_007_10_refresh_is_rejected_after_the_seven_day_absolute_session_lifetime(
    api_client, user
):
    """TC-FR-007-10 — Refresh is rejected after the seven-day absolute session lifetime."""
    with freeze_time(LOGIN_TIME) as frozen:
        login_time = int(frozen().timestamp())
        login(api_client, user.email)
        session_end = login_time + int(timedelta(days=7).total_seconds())

        # Several successful rotations, each before T + 7 days.
        for elapsed in (timedelta(days=2), timedelta(days=4), timedelta(days=6, hours=23)):
            frozen.move_to(LOGIN_TIME)
            frozen.tick(elapsed)
            response = refresh(api_client)
            assert response.status_code == 200
            claims = tokens.decode_refresh_token(refresh_cookie(api_client))
            assert claims["session_start"] == login_time
            assert claims["exp"] == session_end

        frozen.move_to(LOGIN_TIME)
        frozen.tick(timedelta(days=7, seconds=1))
        response = refresh(api_client)

    assert_rejected_without_credentials(response)


def test_tc_fr_007_11_refresh_token_is_signed_with_the_accepted_algorithm_and_claims(
    api_client, user
):
    """TC-FR-007-11 — Refresh token is signed with the accepted algorithm and claim set."""
    response = login(api_client, user.email)
    access_token = response.json()["access_token"]
    refresh_token = refresh_cookie(response)

    header, claims = decode_unverified(refresh_token)
    assert header["alg"] == "HS256"
    assert set(claims) == {"sub", "token_type", "jti", "session_start", "iat", "exp"}
    assert claims["token_type"] == "refresh"
    assert claims["sub"] == str(user.pk)

    csrf_token = bootstrap_csrf(api_client)
    forged = [
        with_header_alg(refresh_token, "none"),
        with_header_alg(refresh_token, "HS512"),
        jwt.encode(claims, django_settings.JWT_SIGNING_KEY, algorithm="HS512"),
        access_token,  # an access token submitted as a refresh token
    ]
    for token in forged:
        set_refresh_cookie(api_client, token)
        assert_rejected_without_credentials(refresh(api_client, csrf_token))

    # The genuine token was never consumed by the rejected attempts.
    set_refresh_cookie(api_client, refresh_token)
    assert refresh(api_client, csrf_token).status_code == 200


def test_tc_sec_001_10_refresh_does_not_require_a_bearer_token(logged_in):
    """TC-SEC-001-10 — Refresh does not require a bearer token."""
    assert "HTTP_AUTHORIZATION" not in logged_in._credentials

    response = refresh(logged_in)

    assert response.status_code not in (401, 403)
    assert response.status_code == 200


def test_tc_sec_007_04_refresh_requests_exceeding_the_limit_are_throttled(logged_in):
    """TC-SEC-007-04 — Refresh requests exceeding the configured limit are throttled."""
    csrf_token = bootstrap_csrf(logged_in)
    for _ in range(30):
        assert refresh(logged_in, csrf_token).status_code == 200

    response = logged_in.post(REFRESH_URL, HTTP_X_CSRFTOKEN=csrf_token)

    assert response.status_code == 429
    assert int(response["Retry-After"]) > 0
    assert "refresh_token" not in response.cookies
