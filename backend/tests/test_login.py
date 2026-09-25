"""Login, CSRF bootstrap and login throttling (Slice 2)."""

import base64
import json
from datetime import timedelta

import jwt
import pytest
from django.conf import settings as django_settings
from django.middleware.csrf import _unmask_cipher_token
from freezegun import freeze_time

from accounts import tokens
from tests.conftest import DEFAULT_PASSWORD
from tests.helpers import (
    CSRF_URL,
    LOGIN_URL,
    bootstrap_csrf,
    decode_unverified,
    login,
    use_cookie_settings_of,
)

pytestmark = pytest.mark.django_db

DEVELOPMENT = "config.settings.development"
PRODUCTION = "config.settings.production"
PROTECTED_URL = "/api/v1/schema/"
INVALID_CREDENTIALS = {"detail": "Invalid credentials."}


@pytest.fixture
def user(make_user):
    return make_user(email="person@example.com")


def with_header_alg(token, alg):
    """Copy `token` with its header `alg` replaced, keeping payload and signature."""
    _, payload, signature = token.split(".")
    header = base64.urlsafe_b64encode(json.dumps({"alg": alg, "typ": "JWT"}).encode())
    return f"{header.rstrip(b'=').decode()}.{payload}.{'' if alg == 'none' else signature}"


def protected_request(client, token):
    return client.get(PROTECTED_URL, HTTP_AUTHORIZATION=f"Bearer {token}")


def test_tc_fr_005_01_valid_credentials_log_in_and_return_an_access_token(api_client, user):
    """TC-FR-005-01 — Valid credentials log in and return an access token."""
    response = login(api_client, user.email)

    assert response.status_code == 200
    assert response.json()["access_token"]
    assert tokens.decode_access_token(response.json()["access_token"])["sub"] == str(user.pk)


def test_tc_fr_005_02_successful_login_sets_the_refresh_token_only_in_the_cookie(api_client, user):
    """TC-FR-005-02 — Successful login sets the refresh token only in the cookie."""
    response = login(api_client, user.email)

    refresh_token = response.cookies["refresh_token"].value
    assert tokens.decode_refresh_token(refresh_token)["sub"] == str(user.pk)
    assert set(response.json()) == {"access_token"}
    assert refresh_token not in response.content.decode()
    assert "refresh" not in response.content.decode()


def test_tc_fr_005_03_login_with_an_unknown_email_returns_a_generic_error(api_client):
    """TC-FR-005-03 — Login with an unknown email returns a generic authentication error."""
    response = login(api_client, "unknown@example.com", "any-password-at-all")

    assert response.status_code == 401
    assert response.json() == INVALID_CREDENTIALS
    assert "refresh_token" not in response.cookies


def test_tc_fr_005_04_login_with_an_incorrect_password_returns_a_generic_error(api_client, user):
    """TC-FR-005-04 — Login with an incorrect password returns a generic authentication error."""
    response = login(api_client, user.email, "not-the-right-password")

    assert response.status_code == 401
    assert response.json() == INVALID_CREDENTIALS
    assert "refresh_token" not in response.cookies


def test_tc_fr_005_05_access_token_expires_ten_minutes_after_issuance(api_client, user):
    """TC-FR-005-05 — Access token expires ten minutes after issuance."""
    issued_at = "2026-08-04T09:00:00+00:00"
    with freeze_time(issued_at) as frozen:
        token = login(api_client, user.email).json()["access_token"]
        _, claims = decode_unverified(token)
        assert claims["exp"] == claims["iat"] + 600
        assert claims["iat"] == int(frozen().timestamp())

        frozen.tick(timedelta(minutes=9, seconds=59))
        assert protected_request(api_client, token).status_code == 200

        frozen.tick(timedelta(seconds=2))  # T + 10 minutes 1 second
        rejected = protected_request(api_client, token)
        assert rejected.status_code == 401


def test_tc_fr_005_07_access_token_is_signed_with_the_accepted_algorithm_and_claims(
    api_client, user
):
    """TC-FR-005-07 — Access token is signed with the accepted algorithm and claim set."""
    response = login(api_client, user.email)
    access_token = response.json()["access_token"]
    refresh_token = response.cookies["refresh_token"].value

    header, claims = decode_unverified(access_token)
    assert header["alg"] == "HS256"
    assert set(claims) == {"sub", "token_type", "iat", "exp"}
    assert claims["token_type"] == "access"
    assert claims["sub"] == str(user.pk)
    assert protected_request(api_client, access_token).status_code == 200

    for alg in ("none", "HS512"):
        assert protected_request(api_client, with_header_alg(access_token, alg)).status_code == 401
    resigned = jwt.encode(claims, django_settings.JWT_SIGNING_KEY, algorithm="HS512")
    assert protected_request(api_client, resigned).status_code == 401

    assert protected_request(api_client, refresh_token).status_code == 401


def test_tc_sec_001_08_csrf_bootstrap_does_not_require_a_bearer_token(api_client):
    """TC-SEC-001-08 — CSRF bootstrap does not require a bearer token."""
    response = api_client.get(CSRF_URL)

    assert response.status_code not in (401, 403)
    assert response.status_code == 200


def test_tc_sec_001_09_login_does_not_require_a_bearer_token(api_client, user):
    """TC-SEC-001-09 — Login does not require a bearer token."""
    response = login(api_client, user.email)

    assert response.status_code not in (401, 403)
    assert response.status_code == 200


def assert_refresh_cookie_attributes(morsel, *, secure, samesite):
    assert morsel["httponly"] is True
    assert morsel["domain"] == ""  # host-only
    assert morsel["path"] == "/api/v1/auth/"
    assert bool(morsel["secure"]) is secure
    assert morsel["samesite"] == samesite
    assert int(morsel["max-age"]) == int(tokens.REFRESH_SESSION_LIFETIME.total_seconds())


def test_tc_sec_005_08_refresh_cookie_carries_its_production_attributes(api_client, user, settings):
    """TC-SEC-005-08 — The refresh-token cookie carries its production attributes."""
    use_cookie_settings_of(settings, PRODUCTION)

    with freeze_time("2026-08-04T09:00:00+00:00"):
        response = login(api_client, user.email)

    assert response.status_code == 200
    assert_refresh_cookie_attributes(
        response.cookies["refresh_token"], secure=True, samesite="None"
    )


def test_tc_sec_005_09_refresh_cookie_carries_its_local_development_attributes(
    api_client, user, settings
):
    """TC-SEC-005-09 — The refresh-token cookie carries its local-development attributes."""
    use_cookie_settings_of(settings, DEVELOPMENT, {})

    with freeze_time("2026-08-04T09:00:00+00:00"):
        response = login(api_client, user.email)

    assert response.status_code == 200
    assert_refresh_cookie_attributes(
        response.cookies["refresh_token"], secure=False, samesite="Lax"
    )


def test_tc_sec_005_10_csrf_bootstrap_sets_the_cookie_and_returns_a_matching_token(
    api_client, user
):
    """TC-SEC-005-10 — The CSRF bootstrap endpoint sets the cookie and returns a matching token."""
    response = api_client.get(CSRF_URL)

    assert response.status_code == 200
    cookie = response.cookies[django_settings.CSRF_COOKIE_NAME]
    token = response.json()["csrf_token"]
    assert _unmask_cipher_token(token) == cookie.value
    # The token passes CSRF validation against that cookie on a protected request...
    assert login(api_client, user.email, csrf_token=token).status_code == 200
    # ...and a request without it does not.
    missing = api_client.post(
        LOGIN_URL, {"email": user.email, "password": DEFAULT_PASSWORD}, format="json"
    )
    assert missing.status_code == 403
    assert missing.json() == {"detail": "CSRF verification failed."}


def test_tc_sec_005_12_csrf_cookie_is_httponly_under_production_configuration(api_client, settings):
    """TC-SEC-005-12 — The CSRF cookie is HttpOnly under production configuration."""
    use_cookie_settings_of(settings, PRODUCTION)

    response = api_client.get(CSRF_URL)

    assert response.cookies[django_settings.CSRF_COOKIE_NAME]["httponly"] is True


def test_tc_sec_005_13_csrf_cookie_is_httponly_under_local_development_configuration(
    api_client, settings
):
    """TC-SEC-005-13 — The CSRF cookie is HttpOnly under local-development configuration."""
    use_cookie_settings_of(settings, DEVELOPMENT, {})

    response = api_client.get(CSRF_URL)

    assert response.cookies[django_settings.CSRF_COOKIE_NAME]["httponly"] is True


def test_tc_sec_005_14_csrf_cookie_uses_its_documented_production_attributes(api_client, settings):
    """TC-SEC-005-14 — The CSRF cookie uses its documented production attributes."""
    production = use_cookie_settings_of(settings, PRODUCTION)
    assert production.CSRF_COOKIE_PATH == "/api/v1/"
    assert production.CSRF_COOKIE_SECURE is True
    assert production.CSRF_COOKIE_SAMESITE == "None"

    cookie = api_client.get(CSRF_URL).cookies[django_settings.CSRF_COOKIE_NAME]
    assert (cookie["path"], cookie["secure"], cookie["samesite"]) == ("/api/v1/", True, "None")


def test_tc_sec_005_15_csrf_cookie_uses_its_documented_local_development_attributes(
    api_client, settings
):
    """TC-SEC-005-15 — The CSRF cookie uses its documented local-development attributes."""
    development = use_cookie_settings_of(settings, DEVELOPMENT, {})
    assert development.CSRF_COOKIE_PATH == "/api/v1/"
    assert development.CSRF_COOKIE_SECURE is False
    assert development.CSRF_COOKIE_SAMESITE == "Lax"

    cookie = api_client.get(CSRF_URL).cookies[django_settings.CSRF_COOKIE_NAME]
    assert cookie["path"] == "/api/v1/"
    assert not cookie["secure"]
    assert cookie["samesite"] == "Lax"


def test_tc_sec_006_02_unknown_email_and_wrong_password_return_identical_failures(api_client, user):
    """TC-SEC-006-02 — An unknown email and an incorrect password return identical login failure responses."""
    unknown = login(api_client, "unknown@example.com", "not-the-right-password")
    wrong_password = login(api_client, user.email, "not-the-right-password")

    assert unknown.status_code == wrong_password.status_code == 401
    assert unknown.content == wrong_password.content
    assert unknown.json() == wrong_password.json() == INVALID_CREDENTIALS
    assert unknown["Content-Type"] == wrong_password["Content-Type"]
    assert set(unknown.cookies) == set(wrong_password.cookies)


def test_tc_sec_007_01_login_requests_exceeding_the_limit_are_throttled(api_client, user):
    """TC-SEC-007-01 — Requests exceeding the configured limit are throttled."""
    csrf_token = bootstrap_csrf(api_client)
    for _ in range(10):
        assert login(api_client, user.email, "wrong-password", csrf_token).status_code == 401

    response = login(api_client, user.email, csrf_token=csrf_token)

    assert response.status_code == 429
    assert int(response["Retry-After"]) > 0
    assert "refresh_token" not in response.cookies


def test_tc_sec_007_02_rate_limit_resets_after_the_throttle_window_elapses(api_client, user):
    """TC-SEC-007-02 — The rate limit resets after the throttle window elapses."""
    with freeze_time("2026-08-04T09:00:00+00:00") as frozen:
        csrf_token = bootstrap_csrf(api_client)
        for _ in range(10):
            login(api_client, user.email, "wrong-password", csrf_token)
        throttled = login(api_client, user.email, csrf_token=csrf_token)
        assert throttled.status_code == 429

        frozen.tick(timedelta(seconds=int(throttled["Retry-After"]) + 1))
        response = login(api_client, user.email, csrf_token=csrf_token)

    assert response.status_code == 200
    assert response.json()["access_token"]
