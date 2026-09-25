"""Registration (Slice 1): FR-001 … FR-004, SEC-001, SEC-003, SEC-007."""

import pytest
from django.conf import global_settings
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password

from accounts.models import User

REGISTER_URL = "/api/v1/auth/register/"
VALID = {
    "email": "person@example.com",
    "password": "correct-horse-battery",  # pragma: allowlist secret
    "timezone": "Asia/Makassar",
}

pytestmark = pytest.mark.django_db


def register(client, **overrides):
    payload = {**VALID, **overrides}
    payload = {key: value for key, value in payload.items() if value is not None}
    return client.post(REGISTER_URL, payload, format="json")


def assert_rejected_with_field_error(response, field):
    assert response.status_code == 400
    assert field in response.json()
    assert response.json()[field]


def test_tc_fr_001_01_registration_with_all_required_fields_creates_an_account(api_client):
    """TC-FR-001-01 — Registration with all required fields creates an account."""
    assert not User.objects.filter(email__iexact=VALID["email"]).exists()

    response = register(api_client)

    assert response.status_code == 201
    body = response.json()
    assert set(body) == {"id", "email", "timezone"}
    assert body["email"] == VALID["email"]
    assert body["timezone"] == VALID["timezone"]
    assert "password" not in body
    user = authenticate(email=VALID["email"], password=VALID["password"])
    assert user is not None and user.pk == body["id"]


def test_tc_fr_002_01_registration_rejects_a_missing_email(api_client):
    """TC-FR-002-01 — Registration rejects a missing email."""
    response = register(api_client, email=None)

    assert_rejected_with_field_error(response, "email")
    assert User.objects.count() == 0


def test_tc_fr_002_02_registration_rejects_a_malformed_email(api_client):
    """TC-FR-002-02 — Registration rejects a malformed email."""
    response = register(api_client, email="not-an-email")

    assert_rejected_with_field_error(response, "email")
    assert User.objects.count() == 0


def test_tc_fr_002_03_registration_rejects_an_already_registered_email_regardless_of_case(
    api_client, make_user
):
    """TC-FR-002-03 — Registration rejects an already-registered email regardless of case."""
    make_user(email="person@example.com")

    response = register(api_client, email="Person@Example.com")

    assert_rejected_with_field_error(response, "email")
    assert User.objects.count() == 1


def test_tc_fr_003_01_registration_rejects_a_missing_password(api_client):
    """TC-FR-003-01 — Registration rejects a missing password."""
    response = register(api_client, password=None)

    assert_rejected_with_field_error(response, "password")
    assert User.objects.count() == 0


def test_tc_fr_003_02_registration_rejects_a_password_shorter_than_eight_characters(api_client):
    """TC-FR-003-02 — Registration rejects a password shorter than eight characters."""
    assert len("short12") == 7

    response = register(api_client, password="short12")

    assert_rejected_with_field_error(response, "password")
    assert User.objects.count() == 0


def test_tc_fr_003_03_registration_rejects_a_password_longer_than_128_characters(api_client):
    """TC-FR-003-03 — Registration rejects a password longer than 128 characters."""
    too_long = "Tq7!mZ" * 21 + "abc"
    assert len(too_long) == 129

    response = register(api_client, password=too_long)

    assert_rejected_with_field_error(response, "password")
    assert User.objects.count() == 0


def test_tc_fr_004_01_registration_rejects_an_unsupported_timezone(api_client):
    """TC-FR-004-01 — Registration rejects an unsupported timezone."""
    response = register(api_client, timezone="Mars/Olympus_Mons")

    assert_rejected_with_field_error(response, "timezone")
    assert User.objects.count() == 0


def test_tc_sec_003_01_stored_passwords_are_hashed_not_stored_in_plaintext(api_client, settings):
    """TC-SEC-003-01 — Stored passwords are hashed, not stored in plaintext."""
    settings.PASSWORD_HASHERS = global_settings.PASSWORD_HASHERS  # the real hashers

    register(api_client)

    stored = User.objects.get(email=VALID["email"]).password
    assert stored != VALID["password"]
    assert VALID["password"] not in stored
    assert check_password(VALID["password"], stored)
    assert stored.startswith("pbkdf2_sha256$")


def test_tc_sec_003_02_registration_rejects_a_commonly_used_password(api_client):
    """TC-SEC-003-02 — Registration rejects a commonly used password."""
    response = register(api_client, password="password123")

    assert_rejected_with_field_error(response, "password")
    assert User.objects.count() == 0


def test_tc_sec_003_03_registration_rejects_an_entirely_numeric_password(api_client):
    """TC-SEC-003-03 — Registration rejects an entirely numeric password."""
    response = register(api_client, password="40718263951")

    assert_rejected_with_field_error(response, "password")
    assert "entirely numeric" in " ".join(response.json()["password"])
    assert User.objects.count() == 0


def test_tc_sec_003_04_registration_rejects_a_password_matching_the_email_address(api_client):
    """TC-SEC-003-04 — Registration rejects a password matching the account's email address."""
    response = register(api_client, email="person.name@example.com", password="person.name@example")

    assert_rejected_with_field_error(response, "password")
    assert "too similar to the email" in " ".join(response.json()["password"])
    assert User.objects.count() == 0


def test_tc_sec_001_07_registration_does_not_require_a_bearer_token(api_client):
    """TC-SEC-001-07 — Registration does not require a bearer token."""
    assert "HTTP_AUTHORIZATION" not in api_client._credentials

    response = register(api_client)

    assert response.status_code not in (401, 403)
    assert response.status_code == 201


def test_tc_sec_007_03_registration_requests_exceeding_the_limit_are_throttled(api_client):
    """TC-SEC-007-03 — Registration requests exceeding the configured limit are throttled."""
    for number in range(10):
        response = register(api_client, email=f"person{number}@example.com")
        assert response.status_code == 201

    response = register(api_client, email="one-too-many@example.com")

    assert response.status_code == 429
    assert int(response["Retry-After"]) > 0
    assert not User.objects.filter(email="one-too-many@example.com").exists()
