"""The API contract exercised over real HTTP (TECH-001, ADS-TECH-001-01).

The test walks every MVP operation of api_contract.md §4–§18 against a live server
with a plain `http.client` connection: no browser, no Django test client, and no
cookie jar. Cookies are stored and sent back only as the contract scopes them, by
their `Path` attribute. Each response is checked twice: against the structures in
api_contract.md, which wins any disagreement, and against the committed
`openapi.yaml`. The walk also has to cover every operation `openapi.yaml` documents,
so neither document can drift from the implementation unnoticed.
"""

import http.client
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from http.cookies import SimpleCookie
from pathlib import Path
from urllib.parse import urlencode, urlsplit
from zoneinfo import ZoneInfo

import jsonschema
import pytest
import yaml
from pytest_django.live_server_helper import LiveServer

from examinations.recurrence_math import add_calendar_months

OPENAPI = yaml.safe_load((Path(__file__).resolve().parents[1] / "openapi.yaml").read_text())

EMAIL = "contract@example.com"
PASSWORD = "contract-passphrase-2026"  # pragma: allowlist secret
NEW_PASSWORD = "renewed-contract-passphrase"  # pragma: allowlist secret
WRONG_PASSWORD = "not-the-password"  # pragma: allowlist secret

ACCOUNT_KEYS = {"id", "email", "timezone"}
CATEGORY_KEYS = {"id", "name", "slug"}
EXAMINATION_KEYS = {
    "id",
    "user_id",
    "category",
    "title",
    "medical_specialty",
    "scheduled_date",
    "scheduled_time",
    "completed_date",
    "status",
    "location",
    "notes",
    "source_occurrence",
    "time_state",
    "created_at",
    "updated_at",
}
REMINDER_KEYS = {
    "id",
    "examination",
    "offset_days",
    "due_date",
    "is_active",
    "created_at",
    "updated_at",
}
RECURRENCE_KEYS = {"id", "examination", "interval", "next_due_date", "created_at", "updated_at"}
CALENDAR_ENTRY_KEYS = {"calendar_date", "state", "examination"}
CALENDAR_EXAMINATION_KEYS = {
    "id",
    "title",
    "category",
    "scheduled_date",
    "scheduled_time",
    "completed_date",
    "status",
    "time_state",
}
DASHBOARD_KEYS = {
    "upcoming",
    "overdue",
    "recently_completed",
    "status_counts",
    "category_counts",
    "uncategorized_count",
    "overdue_count",
}
STATUSES = {"draft", "planned", "completed", "cancelled", "missed"}
CATEGORY_NAMES = {
    "General medical appointment",
    "Dental appointment",
    "Specialist consultation",
    "Laboratory test",
    "Vaccination",
    "Preventive examination",
    "Follow-up",
    "Other",
}

DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME = re.compile(r"^\d{2}:\d{2}:\d{2}$")

CSRF_FAILURE = {"detail": "CSRF verification failed."}
NOT_FOUND = {"detail": "Not found."}


# ---- OpenAPI 3.0 response schemas as JSON Schema ---------------------------------


def _as_json_schema(node):
    """Rewrite OpenAPI 3.0's `nullable: true` into JSON Schema's explicit null type."""
    if isinstance(node, list):
        return [_as_json_schema(item) for item in node]
    if not isinstance(node, dict):
        return node
    converted = {key: _as_json_schema(value) for key, value in node.items() if key != "nullable"}
    if not node.get("nullable"):
        return converted
    if "type" in converted:
        return {**converted, "type": [converted["type"], "null"]}
    return {"anyOf": [converted, {"type": "null"}]}


COMPONENTS = _as_json_schema(OPENAPI["components"])


def documented_response(method, template, status):
    operation = OPENAPI["paths"].get(template, {}).get(method.lower())
    assert operation is not None, f"{method} {template} is missing from openapi.yaml"
    response = operation["responses"].get(str(status))
    assert response is not None, f"{method} {template} → {status} is not in openapi.yaml"
    return response


# ---- A plain HTTP client ------------------------------------------------------------


@dataclass
class Reply:
    status: int
    headers: http.client.HTTPMessage
    body: bytes
    cookies: dict = field(default_factory=dict)

    def json(self):
        assert self.headers.get("Content-Type", "").startswith("application/json")
        return json.loads(self.body)


class ContractClient:
    """JSON over HTTP; cookies sent back only on paths inside their `Path` attribute."""

    def __init__(self, base_url):
        self.origin = urlsplit(base_url)
        self.cookies = {}  # name -> (value, path)
        self.access_token = None
        self.exercised = set()

    def call(self, method, template, body=None, *, query=None, bearer=True, headers=None, **ids):
        path = template.format(**ids) + (f"?{urlencode(query)}" if query else "")
        request_headers = {"Accept": "application/json", **(headers or {})}
        payload = None
        if body is not None:
            payload = json.dumps(body).encode()
            request_headers["Content-Type"] = "application/json"
        if bearer and self.access_token:
            request_headers["Authorization"] = f"Bearer {self.access_token}"
        cookie = "; ".join(
            f"{name}={value}"
            for name, (value, cookie_path) in self.cookies.items()
            if path.startswith(cookie_path)
        )
        if cookie:
            request_headers["Cookie"] = cookie

        connection = http.client.HTTPConnection(self.origin.hostname, self.origin.port, timeout=10)
        try:
            connection.request(method, path, body=payload, headers=request_headers)
            response = connection.getresponse()
            reply = Reply(response.status, response.headers, response.read())
        finally:
            connection.close()

        for header in reply.headers.get_all("Set-Cookie") or []:
            for name, morsel in SimpleCookie(header).items():
                reply.cookies[name] = morsel
                if morsel["max-age"] == "0":
                    self.cookies.pop(name, None)
                else:
                    self.cookies[name] = (morsel.value, morsel["path"] or "/")

        self.exercised.add((method, template))
        self.check_against_openapi(method, template, reply)
        return reply

    @staticmethod
    def check_against_openapi(method, template, reply):
        documented = documented_response(method, template, reply.status)
        if "content" not in documented:
            assert reply.body == b"", f"{method} {template} → {reply.status} must have no body"
            return
        schema = documented["content"]["application/json"]["schema"]
        jsonschema.validate(reply.json(), {**schema, "components": COMPONENTS})
        for header in documented.get("headers", {}):
            assert reply.headers.get(header) is not None, f"{header} header is documented"


# ---- Structure assertions from api_contract.md --------------------------------------


def assert_instant(value):
    assert datetime.fromisoformat(value).tzinfo is not None, value


def assert_category(category):
    assert set(category) == CATEGORY_KEYS
    assert isinstance(category["id"], int)


def assert_examination(examination):
    """api_contract.md §8.1."""
    assert set(examination) == EXAMINATION_KEYS
    assert "category_id" not in examination
    if examination["category"] is not None:
        assert_category(examination["category"])
    for name in ("scheduled_date", "completed_date"):
        assert examination[name] is None or DATE.match(examination[name])
    assert examination["scheduled_time"] is None or TIME.match(examination["scheduled_time"])
    assert examination["status"] in STATUSES
    assert examination["time_state"] in {"upcoming", "overdue", None}
    assert_instant(examination["created_at"])
    assert_instant(examination["updated_at"])


def assert_reminder(reminder):
    """api_contract.md §14."""
    assert set(reminder) == REMINDER_KEYS
    assert reminder["due_date"] is None or DATE.match(reminder["due_date"])
    assert isinstance(reminder["is_active"], bool)
    assert_instant(reminder["created_at"])
    assert_instant(reminder["updated_at"])


def assert_recurrence(rule):
    """api_contract.md §15."""
    assert set(rule) == RECURRENCE_KEYS
    assert rule["interval"] in {"monthly", "six_months", "yearly"}
    assert rule["next_due_date"] is None or DATE.match(rule["next_due_date"])
    assert_instant(rule["created_at"])
    assert_instant(rule["updated_at"])


def assert_calendar_entry(entry):
    """api_contract.md §17."""
    assert set(entry) == CALENDAR_ENTRY_KEYS
    assert DATE.match(entry["calendar_date"])
    assert entry["state"] in {"planned", "completed", "cancelled", "missed", "overdue"}
    assert set(entry["examination"]) == CALENDAR_EXAMINATION_KEYS


def assert_refresh_cookie(morsel):
    """api_contract.md §5.7, local HTTP development row."""
    assert morsel["httponly"] is True
    assert morsel["path"] == "/api/v1/auth/"
    assert morsel["samesite"] == "Lax"
    assert not morsel["secure"]
    assert not morsel["domain"], "the refresh cookie is host-only"


def ids(items):
    return [item["id"] for item in items]


# ---- The walk ------------------------------------------------------------------------


@pytest.fixture
def api_server(settings):
    """A live HTTP server running the API in a thread, for this test only.

    The API serves no static files, so `STATIC_URL` is unset; Django's live-server
    static handler still parses it and needs a string.
    """
    settings.STATIC_URL = "/static/"
    server = LiveServer("localhost")
    yield server
    server.stop()


@pytest.mark.django_db(transaction=True, serialized_rollback=True)
def test_tc_tech_001_01_every_documented_endpoint_matches_its_contract_over_http(api_server):
    """TC-TECH-001-01 — Every documented endpoint matches its contract without browser-specific behavior."""
    client = ContractClient(api_server.url)

    # §4 Health check.
    reply = client.call("GET", "/api/v1/health/", bearer=False)
    assert reply.status == 200 and reply.json() == {"status": "ok"}

    # §5.2 Register; §3.4 field-level validation failure.
    reply = client.call(
        "POST", "/api/v1/auth/register/", {"email": EMAIL, "password": PASSWORD}, bearer=False
    )
    assert reply.status == 400 and set(reply.json()) == {"timezone"}
    assert all(isinstance(message, str) for message in reply.json()["timezone"])
    reply = client.call(
        "POST",
        "/api/v1/auth/register/",
        {"email": EMAIL, "password": PASSWORD, "timezone": "Asia/Makassar"},
        bearer=False,
    )
    assert reply.status == 201
    account = reply.json()
    assert set(account) == ACCOUNT_KEYS
    assert account["email"] == EMAIL and account["timezone"] == "Asia/Makassar"

    # §5.3 CSRF bootstrap: the token in the body, the cookie HttpOnly and scoped to the API.
    reply = client.call("GET", "/api/v1/auth/csrf/", bearer=False)
    assert reply.status == 200 and set(reply.json()) == {"csrf_token"}
    csrf = {"X-CSRFToken": reply.json()["csrf_token"]}
    csrf_cookie = reply.cookies["csrftoken"]
    assert csrf_cookie["httponly"] is True and csrf_cookie["path"] == "/api/v1/"
    assert csrf_cookie["samesite"] == "Lax" and not csrf_cookie["secure"]

    # §5.4 Log in: CSRF failure, invalid credentials, success.
    credentials = {"email": EMAIL, "password": PASSWORD}
    reply = client.call("POST", "/api/v1/auth/login/", credentials, bearer=False)
    assert reply.status == 403 and reply.json() == CSRF_FAILURE
    assert "refresh_token" not in reply.cookies
    reply = client.call(
        "POST",
        "/api/v1/auth/login/",
        {"email": EMAIL, "password": WRONG_PASSWORD},
        bearer=False,
        headers=csrf,
    )
    assert reply.status == 401 and reply.json() == {"detail": "Invalid credentials."}
    reply = client.call("POST", "/api/v1/auth/login/", credentials, bearer=False, headers=csrf)
    assert reply.status == 200 and set(reply.json()) == {"access_token"}
    assert_refresh_cookie(reply.cookies["refresh_token"])
    # Aligned with the seven-day refresh-token expiry (§5.7), give or take a clock tick.
    assert 0 <= 7 * 24 * 60 * 60 - int(reply.cookies["refresh_token"]["max-age"]) <= 5
    client.access_token = reply.json()["access_token"]

    # §3.1 A protected operation without the bearer token.
    reply = client.call("GET", "/api/v1/account/", bearer=False)
    assert reply.status == 401 and set(reply.json()) == {"detail"}

    # §6 Account.
    reply = client.call("GET", "/api/v1/account/")
    assert reply.status == 200 and reply.json() == account
    reply = client.call("PATCH", "/api/v1/account/", {"timezone": "Europe/Warsaw"})
    assert reply.status == 200 and reply.json() == {**account, "timezone": "Europe/Warsaw"}
    today = datetime.now(ZoneInfo("Europe/Warsaw")).date()
    reply = client.call(
        "POST",
        "/api/v1/account/password/",
        {"current_password": WRONG_PASSWORD, "new_password": NEW_PASSWORD},
    )
    assert reply.status == 400 and set(reply.json()) == {"current_password"}
    reply = client.call(
        "POST",
        "/api/v1/account/password/",
        {"current_password": PASSWORD, "new_password": NEW_PASSWORD},
    )
    assert reply.status == 200 and reply.body == b""

    # §7 Categories.
    reply = client.call("GET", "/api/v1/categories/")
    assert reply.status == 200
    categories = reply.json()
    for category in categories:
        assert_category(category)
    assert {category["name"] for category in categories} == CATEGORY_NAMES
    dental = next(c for c in categories if c["slug"] == "dental-appointment")

    # §10 Create examination: the documented request shapes, and a read-only field rejected.
    future = today + timedelta(days=40)
    soon = today + timedelta(days=3)
    past = today - timedelta(days=10)
    reply = client.call(
        "POST",
        "/api/v1/examinations/",
        {
            "category_id": dental["id"],
            "title": "Annual dental checkup",
            "medical_specialty": "Dentistry",
            "scheduled_date": future.isoformat(),
            "scheduled_time": "10:30:00",
            "status": "planned",
            "location": "Central Dental Clinic",
            "notes": "Routine appointment",
        },
    )
    assert reply.status == 201
    checkup = reply.json()
    assert_examination(checkup)
    assert checkup["category"] == dental and checkup["user_id"] == account["id"]
    assert checkup["time_state"] == "upcoming" and checkup["source_occurrence"] is None

    reply = client.call(
        "POST", "/api/v1/examinations/", {"title": "Annual eye examination", "status": "draft"}
    )
    assert reply.status == 201
    draft = reply.json()
    assert_examination(draft)
    assert draft["category"] is None and draft["scheduled_date"] is None
    assert draft["time_state"] is None

    reply = client.call(
        "POST",
        "/api/v1/examinations/",
        {"title": "Blood test", "status": "planned", "scheduled_date": soon.isoformat()},
    )
    assert reply.status == 201
    blood_test = reply.json()

    reply = client.call(
        "POST",
        "/api/v1/examinations/",
        {"title": "Missed follow-up", "status": "planned", "scheduled_date": past.isoformat()},
    )
    assert reply.status == 201 and reply.json()["time_state"] == "overdue"
    overdue = reply.json()

    reply = client.call(
        "POST",
        "/api/v1/examinations/",
        {"title": "Vaccination", "status": "completed", "completed_date": past.isoformat()},
    )
    assert reply.status == 201 and reply.json()["time_state"] is None
    completed = reply.json()

    reply = client.call(
        "POST",
        "/api/v1/examinations/",
        {"title": "Not mine", "status": "draft", "user_id": account["id"] + 1},
    )
    assert reply.status == 400 and set(reply.json()) == {"user_id"}

    # §9 List examinations and its filters.
    reply = client.call("GET", "/api/v1/examinations/")
    assert reply.status == 200
    for examination in reply.json():
        assert_examination(examination)
    assert sorted(ids(reply.json())) == sorted(
        ids([checkup, draft, blood_test, overdue, completed])
    )
    queries = {
        "status=planned": ({"status": "planned"}, [checkup, blood_test, overdue]),
        "category": ({"category": dental["id"]}, [checkup]),
        "search": ({"search": "DENTAL"}, [checkup]),
        "time_state=past": ({"time_state": "past"}, [completed]),
        "time_state=upcoming": ({"time_state": "upcoming"}, [checkup, blood_test]),
        "time_state=overdue": ({"time_state": "overdue"}, [overdue]),
    }
    for label, (query, expected) in queries.items():
        reply = client.call("GET", "/api/v1/examinations/", query=query)
        assert reply.status == 200, label
        assert sorted(ids(reply.json())) == sorted(ids(expected)), label
    reply = client.call("GET", "/api/v1/examinations/", query={"ordering": "scheduled_date"})
    assert ids(reply.json()) == ids([overdue, blood_test, checkup, draft, completed])
    reply = client.call("GET", "/api/v1/examinations/", query={"ordering": "-scheduled_date"})
    assert ids(reply.json()) == ids([checkup, blood_test, overdue, draft, completed])
    reply = client.call("GET", "/api/v1/examinations/", query={"status": "someday"})
    assert reply.status == 400 and set(reply.json()) == {"status"}

    # §11 Retrieve; §3.3 not found.
    reply = client.call("GET", "/api/v1/examinations/{id}/", id=checkup["id"])
    assert reply.status == 200 and reply.json() == checkup
    reply = client.call("GET", "/api/v1/examinations/{id}/", id=10**9)
    assert reply.status == 404 and reply.json() == NOT_FOUND

    # §12 Update: draft to planned; §3.4 a resulting-record rule.
    reply = client.call(
        "PATCH", "/api/v1/examinations/{id}/", {"status": "completed"}, id=draft["id"]
    )
    assert reply.status == 400 and set(reply.json()) == {"completed_date"}
    reply = client.call(
        "PATCH",
        "/api/v1/examinations/{id}/",
        {"status": "planned", "scheduled_date": future.isoformat()},
        id=draft["id"],
    )
    assert reply.status == 200
    assert_examination(reply.json())
    assert reply.json()["status"] == "planned" and reply.json()["time_state"] == "upcoming"

    # §14 Reminder: create, the due list, update, disable, re-enable, retrieve.
    reminder_path = "/api/v1/examinations/{id}/reminder/"
    reply = client.call("GET", reminder_path, id=blood_test["id"])
    assert reply.status == 404 and reply.json() == NOT_FOUND
    reply = client.call("POST", reminder_path, {"offset_days": 7}, id=blood_test["id"])
    assert reply.status == 201
    reminder = reply.json()
    assert_reminder(reminder)
    assert reminder["examination"] == blood_test["id"] and reminder["is_active"] is True
    assert reminder["due_date"] == (soon - timedelta(days=7)).isoformat()
    reply = client.call("POST", reminder_path, {"offset_days": 1}, id=blood_test["id"])
    assert reply.status == 400 and set(reply.json()) == {"non_field_errors"}

    reply = client.call("GET", "/api/v1/reminders/", query={"state": "due"})
    assert reply.status == 200 and reply.json() == [reminder]
    reply = client.call("GET", "/api/v1/reminders/", query={"state": "all"})
    assert reply.status == 400 and set(reply.json()) == {"state"}

    reply = client.call("PATCH", reminder_path, {"offset_days": 3}, id=blood_test["id"])
    assert reply.status == 200
    assert_reminder(reply.json())
    assert reply.json()["due_date"] == today.isoformat()
    reply = client.call("PATCH", reminder_path, {"is_active": False}, id=blood_test["id"])
    assert reply.status == 200 and reply.json()["is_active"] is False
    reply = client.call("PATCH", reminder_path, {"is_active": True}, id=blood_test["id"])
    assert reply.status == 200 and reply.json()["is_active"] is True
    reply = client.call("GET", reminder_path, id=blood_test["id"])
    assert reply.status == 200 and reply.json()["offset_days"] == 3

    # §15 Recurrence: create, update, retrieve.
    recurrence_path = "/api/v1/examinations/{id}/recurrence/"
    reply = client.call("GET", recurrence_path, id=checkup["id"])
    assert reply.status == 404 and reply.json() == NOT_FOUND
    reply = client.call("POST", recurrence_path, {"interval": "yearly"}, id=checkup["id"])
    assert reply.status == 201
    assert_recurrence(reply.json())
    assert reply.json()["next_due_date"] == add_calendar_months(future, 12).isoformat()
    reply = client.call("POST", recurrence_path, {"interval": "weekly"}, id=blood_test["id"])
    assert reply.status == 400 and set(reply.json()) == {"interval"}
    reply = client.call("PATCH", recurrence_path, {"interval": "six_months"}, id=checkup["id"])
    assert reply.status == 200
    rule = reply.json()
    assert_recurrence(rule)
    assert rule["next_due_date"] == add_calendar_months(future, 6).isoformat()
    reply = client.call("GET", recurrence_path, id=checkup["id"])
    assert reply.status == 200 and reply.json() == rule

    # §16 Next occurrence: 201 when created, 200 with the same record when repeated.
    next_path = "/api/v1/examinations/{id}/next-occurrence/"
    reply = client.call("POST", next_path, id=checkup["id"])
    assert reply.status == 201
    occurrence = reply.json()
    assert_examination(occurrence)
    assert occurrence["source_occurrence"] == checkup["id"]
    assert occurrence["status"] == "planned"
    assert occurrence["scheduled_date"] == rule["next_due_date"]
    for copied in ("title", "category", "medical_specialty", "scheduled_time", "location"):
        assert occurrence[copied] == checkup[copied], copied
    assert occurrence["notes"] is None and occurrence["completed_date"] is None
    reply = client.call("POST", next_path, id=checkup["id"])
    assert reply.status == 200 and reply.json()["id"] == occurrence["id"]
    reply = client.call("POST", next_path, id=completed["id"])
    assert reply.status == 400 and set(reply.json()) == {"non_field_errors"}

    # §17 Calendar.
    window = {"start_date": past.isoformat(), "end_date": future.isoformat()}
    reply = client.call("GET", "/api/v1/calendar/", query=window)
    assert reply.status == 200
    for entry in reply.json():
        assert_calendar_entry(entry)
    states = {entry["examination"]["id"]: entry["state"] for entry in reply.json()}
    assert states == {
        checkup["id"]: "planned",
        draft["id"]: "planned",
        blood_test["id"]: "planned",
        overdue["id"]: "overdue",
        completed["id"]: "completed",
    }
    reply = client.call("GET", "/api/v1/calendar/", query={"start_date": past.isoformat()})
    assert reply.status == 400 and set(reply.json()) == {"end_date"}

    # §18 Dashboard.
    reply = client.call("GET", "/api/v1/dashboard/")
    assert reply.status == 200
    dashboard = reply.json()
    assert set(dashboard) == DASHBOARD_KEYS
    for collection in ("upcoming", "overdue", "recently_completed"):
        for examination in dashboard[collection]:
            assert_examination(examination)
    assert ids(dashboard["overdue"]) == [overdue["id"]]
    assert ids(dashboard["recently_completed"]) == [completed["id"]]
    assert dashboard["status_counts"] == {
        "draft": 0,
        "planned": 5,
        "completed": 1,
        "cancelled": 0,
        "missed": 0,
    }
    assert len(dashboard["category_counts"]) == len(CATEGORY_NAMES)
    for item in dashboard["category_counts"]:
        assert set(item) == {"category", "count"}
        assert_category(item["category"])
    counts = {item["category"]["slug"]: item["count"] for item in dashboard["category_counts"]}
    assert counts["dental-appointment"] == 2
    assert dashboard["uncategorized_count"] == 4
    assert dashboard["overdue_count"] == 1

    # §13 Delete: an empty 204; the recurrence rule cascades; the occurrence survives.
    reply = client.call("DELETE", "/api/v1/examinations/{id}/", id=checkup["id"])
    assert reply.status == 204 and reply.body == b""
    reply = client.call("GET", recurrence_path, id=checkup["id"])
    assert reply.status == 404
    reply = client.call("GET", "/api/v1/examinations/{id}/", id=occurrence["id"])
    assert reply.status == 200 and reply.json()["source_occurrence"] is None

    # §5.5 Refresh: CSRF failure, then rotation to a new refresh cookie.
    reply = client.call("POST", "/api/v1/auth/refresh/", bearer=False)
    assert reply.status == 403 and reply.json() == CSRF_FAILURE
    first_refresh = client.cookies["refresh_token"][0]
    reply = client.call("POST", "/api/v1/auth/refresh/", bearer=False, headers=csrf)
    assert reply.status == 200 and set(reply.json()) == {"access_token"}
    assert_refresh_cookie(reply.cookies["refresh_token"])
    assert reply.cookies["refresh_token"].value != first_refresh
    client.access_token = reply.json()["access_token"]
    reply = client.call("GET", "/api/v1/account/")
    assert reply.status == 200

    # §5.6 Log out: an empty 204 and a cleared cookie; the logged-out token is then refused.
    logged_out_token = client.cookies["refresh_token"][0]
    reply = client.call("POST", "/api/v1/auth/logout/", bearer=False)
    assert reply.status == 403 and reply.json() == CSRF_FAILURE
    reply = client.call("POST", "/api/v1/auth/logout/", bearer=False, headers=csrf)
    assert reply.status == 204 and reply.body == b""
    assert_refresh_cookie(reply.cookies["refresh_token"])
    assert reply.cookies["refresh_token"]["max-age"] == "0"
    assert "refresh_token" not in client.cookies
    client.cookies["refresh_token"] = (logged_out_token, "/api/v1/auth/")
    reply = client.call("POST", "/api/v1/auth/refresh/", bearer=False, headers=csrf)
    assert reply.status == 401
    assert reply.json() == {"detail": "Refresh token is invalid or expired."}
    assert reply.cookies["refresh_token"]["max-age"] == "0"

    # §3.5 Rate limit exceeded: a 429 with Retry-After once the login limit is used up.
    for _ in range(11):
        reply = client.call("POST", "/api/v1/auth/login/", credentials, bearer=False, headers=csrf)
        if reply.status == 429:
            break
    assert reply.status == 429
    assert set(reply.json()) == {"detail"}
    assert int(reply.headers["Retry-After"]) > 0

    # Every operation openapi.yaml documents was exercised, and nothing else.
    documented = {
        (method.upper(), template)
        for template, operations in OPENAPI["paths"].items()
        for method in operations
        if method in {"get", "post", "patch", "put", "delete"}
    }
    assert client.exercised == documented


def test_openapi_documents_exactly_the_contract_operations():
    """Supports TC-TECH-001-01: the operation list of api_contract.md §4–§18."""
    contract = {
        ("GET", "/api/v1/health/"),
        ("POST", "/api/v1/auth/register/"),
        ("GET", "/api/v1/auth/csrf/"),
        ("POST", "/api/v1/auth/login/"),
        ("POST", "/api/v1/auth/refresh/"),
        ("POST", "/api/v1/auth/logout/"),
        ("GET", "/api/v1/account/"),
        ("PATCH", "/api/v1/account/"),
        ("POST", "/api/v1/account/password/"),
        ("GET", "/api/v1/categories/"),
        ("GET", "/api/v1/examinations/"),
        ("POST", "/api/v1/examinations/"),
        ("GET", "/api/v1/examinations/{id}/"),
        ("PATCH", "/api/v1/examinations/{id}/"),
        ("DELETE", "/api/v1/examinations/{id}/"),
        ("GET", "/api/v1/examinations/{id}/reminder/"),
        ("POST", "/api/v1/examinations/{id}/reminder/"),
        ("PATCH", "/api/v1/examinations/{id}/reminder/"),
        ("GET", "/api/v1/reminders/"),
        ("GET", "/api/v1/examinations/{id}/recurrence/"),
        ("POST", "/api/v1/examinations/{id}/recurrence/"),
        ("PATCH", "/api/v1/examinations/{id}/recurrence/"),
        ("POST", "/api/v1/examinations/{id}/next-occurrence/"),
        ("GET", "/api/v1/calendar/"),
        ("GET", "/api/v1/dashboard/"),
    }
    documented = {
        (method.upper(), template)
        for template, operations in OPENAPI["paths"].items()
        for method in operations
        if method in {"get", "post", "patch", "put", "delete"}
    }
    assert documented == contract
