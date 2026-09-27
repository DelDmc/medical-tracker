"""Account retrieval and timezone update (Slice 5)."""

import pytest

from tests.helpers import authenticate_as

pytestmark = pytest.mark.django_db

ACCOUNT_URL = "/api/v1/account/"


@pytest.fixture
def user(make_user):
    return make_user(email="person@example.com", timezone="Asia/Makassar")


def test_tc_fr_009_01_updating_the_account_timezone_persists_the_new_value(api_client, user):
    """TC-FR-009-01 — Updating the account timezone persists the new value."""
    authenticate_as(api_client, user)

    response = api_client.patch(ACCOUNT_URL, {"timezone": "Europe/Warsaw"}, format="json")

    assert response.status_code == 200
    assert response.json() == {"id": user.pk, "email": user.email, "timezone": "Europe/Warsaw"}
    confirmed = api_client.get(ACCOUNT_URL)
    assert confirmed.status_code == 200
    assert confirmed.json()["timezone"] == "Europe/Warsaw"
    user.refresh_from_db()
    assert user.timezone == "Europe/Warsaw"


def test_tc_fr_009_02_updating_the_account_timezone_rejects_an_unsupported_value(api_client, user):
    """TC-FR-009-02 — Updating the account timezone rejects an unsupported value."""
    authenticate_as(api_client, user)

    response = api_client.patch(ACCOUNT_URL, {"timezone": "Atlantis/Lost_City"}, format="json")

    assert response.status_code == 400
    assert response.json()["timezone"]
    user.refresh_from_db()
    assert user.timezone == "Asia/Makassar"
    assert api_client.get(ACCOUNT_URL).json()["timezone"] == "Asia/Makassar"


def test_tc_sec_001_06_unauthenticated_requests_to_the_account_endpoint_are_rejected(api_client):
    """TC-SEC-001-06 — Unauthenticated requests to the account endpoint are rejected."""
    response = api_client.get(ACCOUNT_URL)

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication credentials were not provided."}
