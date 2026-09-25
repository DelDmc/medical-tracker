"""Logout (Slice 4)."""

from datetime import timedelta

import pytest
from freezegun import freeze_time

from accounts import tokens
from accounts.models import RevokedRefreshToken, revoke_refresh_token
from tests.helpers import login, logout, refresh, refresh_cookie, set_refresh_cookie

pytestmark = pytest.mark.django_db

LOGIN_TIME = "2026-08-01T09:00:00+00:00"
PROTECTED_URL = "/api/v1/schema/"


@pytest.fixture
def user(make_user):
    return make_user(email="person@example.com")


@pytest.fixture
def logged_in(api_client, user):
    assert login(api_client, user.email).status_code == 200
    return api_client


def assert_empty_204(response):
    assert response.status_code == 204
    assert response.content == b""


def assert_cookie_cleared(response):
    cleared = response.cookies["refresh_token"]
    assert cleared.value == ""
    assert int(cleared["max-age"]) == 0
    assert cleared["path"] == "/api/v1/auth/"
    assert cleared["domain"] == ""
    assert cleared["httponly"] is True
    assert not cleared["secure"]  # local development configuration
    assert cleared["samesite"] == "Lax"


def test_tc_fr_006_01_logout_invalidates_the_refresh_token(logged_in):
    """TC-FR-006-01 — Logout invalidates the refresh token."""
    refresh_token = refresh_cookie(logged_in)

    assert logout(logged_in).status_code == 204

    set_refresh_cookie(logged_in, refresh_token)
    response = refresh(logged_in)
    assert response.status_code == 401
    assert "access_token" not in response.json()


def test_tc_fr_006_02_logout_clears_the_refresh_token_cookie(logged_in):
    """TC-FR-006-02 — Logout clears the refresh-token cookie."""
    response = logout(logged_in)

    assert_cookie_cleared(response)


def test_tc_fr_006_03_logout_with_a_valid_refresh_token_returns_an_empty_204(logged_in):
    """TC-FR-006-03 — Logout with a valid refresh token returns an empty 204 response."""
    jti = tokens.decode_refresh_token(refresh_cookie(logged_in))["jti"]

    response = logout(logged_in)

    assert_empty_204(response)
    assert RevokedRefreshToken.objects.filter(jti=jti).exists()


def test_tc_fr_006_04_logout_is_idempotent_for_a_missing_refresh_token(api_client):
    """TC-FR-006-04 — Logout is idempotent for a missing refresh token."""
    assert "refresh_token" not in api_client.cookies

    response = logout(api_client)

    assert_empty_204(response)
    assert_cookie_cleared(response)


def test_tc_fr_006_05_logout_is_idempotent_for_an_expired_refresh_token(api_client, user):
    """TC-FR-006-05 — Logout is idempotent for an expired refresh token."""
    with freeze_time(LOGIN_TIME) as frozen:
        login(api_client, user.email)
        frozen.tick(timedelta(days=8))

        response = logout(api_client)

    assert_empty_204(response)
    assert_cookie_cleared(response)


def test_tc_fr_006_06_logout_is_idempotent_for_a_revoked_refresh_token(logged_in):
    """TC-FR-006-06 — Logout is idempotent for a revoked refresh token."""
    revoke_refresh_token(tokens.decode_refresh_token(refresh_cookie(logged_in)))

    response = logout(logged_in)

    assert_empty_204(response)
    assert_cookie_cleared(response)
    assert RevokedRefreshToken.objects.count() == 1


def test_tc_fr_006_07_logout_is_idempotent_for_an_already_invalid_refresh_token(api_client):
    """TC-FR-006-07 — Logout is idempotent for an already-invalid refresh token."""
    set_refresh_cookie(api_client, "this.is-not.a-valid-token")

    response = logout(api_client)

    assert_empty_204(response)
    assert_cookie_cleared(response)
    assert RevokedRefreshToken.objects.count() == 0


def test_tc_fr_006_14_a_pre_logout_access_token_remains_valid_until_its_own_expiration(
    api_client, user
):
    """TC-FR-006-14 — A pre-logout access token remains valid until its own expiration."""
    with freeze_time(LOGIN_TIME) as frozen:
        access_token = login(api_client, user.email).json()["access_token"]
        assert logout(api_client).status_code == 204
        frozen.tick(timedelta(minutes=9))

        response = api_client.get(PROTECTED_URL, HTTP_AUTHORIZATION=f"Bearer {access_token}")

    assert response.status_code == 200
