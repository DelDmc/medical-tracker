"""Authenticated password change (Slice 6)."""

import pytest

from accounts.models import User
from tests.conftest import DEFAULT_PASSWORD
from tests.helpers import authenticate_as, login

pytestmark = pytest.mark.django_db

PASSWORD_URL = "/api/v1/account/password/"
NEW_PASSWORD = "a-brand-new-passphrase"  # pragma: allowlist secret
WRONG_PASSWORD = "not-my-password"  # pragma: allowlist secret


@pytest.fixture
def user(make_user):
    return make_user(email="person@example.com")


def stored_hash(user):
    return User.objects.get(pk=user.pk).password


def test_tc_fr_048_01_password_change_succeeds_with_correct_and_compliant_passwords(
    api_client, user
):
    """TC-FR-048-01 — Password change succeeds with a correct current password and a compliant new password."""
    authenticate_as(api_client, user)

    response = api_client.post(
        PASSWORD_URL,
        {"current_password": DEFAULT_PASSWORD, "new_password": NEW_PASSWORD},
        format="json",
    )

    assert response.status_code == 200
    assert response.content == b""
    api_client.credentials()
    assert login(api_client, user.email, DEFAULT_PASSWORD).status_code == 401
    assert login(api_client, user.email, NEW_PASSWORD).status_code == 200


def test_tc_fr_048_02_password_change_is_rejected_for_an_incorrect_current_password(
    api_client, user
):
    """TC-FR-048-02 — Password change is rejected for an incorrect current password."""
    authenticate_as(api_client, user)
    before = stored_hash(user)

    response = api_client.post(
        PASSWORD_URL,
        {"current_password": WRONG_PASSWORD, "new_password": NEW_PASSWORD},
        format="json",
    )

    assert response.status_code == 400
    assert response.json()["current_password"]
    assert stored_hash(user) == before


def test_tc_fr_048_03_password_change_is_rejected_when_the_new_password_fails_the_policy(
    api_client, user
):
    """TC-FR-048-03 — Password change is rejected when the new password fails the accepted policy."""
    authenticate_as(api_client, user)
    before = stored_hash(user)

    for failing in ("short12", "password123", "40718263951", "person@example.com"):
        response = api_client.post(
            PASSWORD_URL,
            {"current_password": DEFAULT_PASSWORD, "new_password": failing},
            format="json",
        )
        assert response.status_code == 400, failing
        assert response.json()["new_password"], failing
        assert stored_hash(user) == before
