"""Deployment integration and smoke tests (SEC-005, TECH-006).

These run against the deployed backend and frontend, never against the local test
server. Every test here is skipped unless both environment variables are set:

    DEPLOYMENT_BASE_URL         the backend origin, e.g. https://<service>.onrender.com
    DEPLOYMENT_FRONTEND_ORIGIN  the frontend origin, e.g. https://<project>.vercel.app

The requests use only the standard library over HTTPS. Cookies are handled by hand and
no redirect is followed. The primary-flow test registers a throwaway account on the
deployment, with an address under example.com and a random password.
"""

import http.client
import json
import os
import re
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from http.cookies import SimpleCookie
from urllib.parse import urljoin, urlsplit
from zoneinfo import ZoneInfo

import pytest

BASE_URL = os.environ.get("DEPLOYMENT_BASE_URL", "").rstrip("/")
FRONTEND_ORIGIN = os.environ.get("DEPLOYMENT_FRONTEND_ORIGIN", "").rstrip("/")
# An origin that is in neither the CORS allowlist nor the CSRF trusted origins.
UNCONFIGURED_ORIGIN = "https://unconfigured-origin.example"
TIMEZONE = "Europe/Warsaw"
# Generous on purpose: a sleeping instance's first request has to cold-start.
TIMEOUT = 120

pytestmark = [
    pytest.mark.deployment,
    pytest.mark.skipif(
        not (BASE_URL and FRONTEND_ORIGIN),
        reason="set DEPLOYMENT_BASE_URL and DEPLOYMENT_FRONTEND_ORIGIN to test a deployment",
    ),
]

CSRF_FAILURE = {"detail": "CSRF verification failed."}


@dataclass
class Reply:
    status: int
    headers: http.client.HTTPMessage
    body: bytes
    cookies: dict = field(default_factory=dict)

    def json(self):
        return json.loads(self.body)

    def header_values(self, name):
        return {value.strip().lower() for value in (self.headers.get(name) or "").split(",")}


def send(method, url, body=None, headers=None):
    """One HTTPS request; redirects are returned, not followed."""
    parts = urlsplit(url)
    assert parts.scheme == "https", f"{url} is not an HTTPS URL"
    request_headers = {"Accept": "application/json", **(headers or {})}
    payload = None
    if body is not None:
        payload = json.dumps(body).encode()
        request_headers["Content-Type"] = "application/json"
    connection = http.client.HTTPSConnection(parts.hostname, parts.port, timeout=TIMEOUT)
    try:
        target = parts.path + (f"?{parts.query}" if parts.query else "")
        connection.request(method, target or "/", body=payload, headers=request_headers)
        response = connection.getresponse()
        reply = Reply(response.status, response.headers, response.read())
    finally:
        connection.close()
    for header in reply.headers.get_all("Set-Cookie") or []:
        # Python 3.12's parser drops a whole line that carries an attribute it does not
        # know, such as `Partitioned` (ADS-SEC-005-09), so that one is removed first.
        attributes = [part.strip() for part in header.split(";")]
        kept = [part for part in attributes if part.lower() != "partitioned"]
        reply.cookies.update(SimpleCookie("; ".join(kept)))
    location = reply.headers.get("Location")
    if location:
        assert urljoin(url, location).startswith("https://"), f"redirect to plain HTTP: {location}"
    return reply


class Session:
    """An API client acting from one origin; cookies go back only within their `Path`."""

    def __init__(self, origin):
        self.origin = origin
        self.cookies = {}
        self.csrf_token = None
        self.access_token = None

    def call(self, method, path, body=None, *, csrf=False, bearer=False):
        headers = {"Origin": self.origin}
        cookie = "; ".join(
            f"{name}={morsel.value}"
            for name, morsel in self.cookies.items()
            if path.startswith(morsel["path"] or "/")
        )
        if cookie:
            headers["Cookie"] = cookie
        if csrf:
            headers["X-CSRFToken"] = self.csrf_token
        if bearer:
            headers["Authorization"] = f"Bearer {self.access_token}"
        reply = send(method, BASE_URL + path, body, headers)
        for name, morsel in reply.cookies.items():
            if morsel["max-age"] == "0":
                self.cookies.pop(name, None)
            else:
                self.cookies[name] = morsel
        return reply

    def bootstrap_csrf(self):
        reply = self.call("GET", "/api/v1/auth/csrf/")
        assert reply.status == 200
        self.csrf_token = reply.json()["csrf_token"]
        return reply


@pytest.fixture(scope="module")
def account():
    """A throwaway account registered on the deployment for this run."""
    email = f"deployment-check-{int(time.time())}-{secrets.token_hex(3)}@example.com"
    password = secrets.token_urlsafe(18)
    reply = Session(FRONTEND_ORIGIN).call(
        "POST",
        "/api/v1/auth/register/",
        {"email": email, "password": password, "timezone": TIMEZONE},
    )
    assert reply.status == 201, reply.body
    return {"email": email, "password": password}


# ---- SEC-005: CORS and CSRF from the configured origin only ---------------------------


def test_tc_sec_005_01_a_configured_frontend_origin_is_accepted():
    """TC-SEC-005-01 — A configured frontend origin is accepted."""
    reply = Session(FRONTEND_ORIGIN).call("GET", "/api/v1/auth/csrf/")

    assert reply.status == 200
    assert reply.headers.get("Access-Control-Allow-Origin") == FRONTEND_ORIGIN
    assert reply.headers.get("Access-Control-Allow-Credentials") == "true"


def test_tc_sec_005_02_an_unconfigured_origin_is_rejected():
    """TC-SEC-005-02 — An unconfigured origin is rejected."""
    reply = Session(UNCONFIGURED_ORIGIN).call("GET", "/api/v1/auth/csrf/")

    # Without an allow-origin grant the browser withholds the response from the page.
    assert reply.headers.get("Access-Control-Allow-Origin") is None
    assert reply.headers.get("Access-Control-Allow-Credentials") is None


def test_tc_sec_005_04_preflight_responses_permit_the_required_credentialed_headers():
    """TC-SEC-005-04 — Preflight responses permit the required credentialed headers."""
    reply = send(
        "OPTIONS",
        BASE_URL + "/api/v1/auth/login/",
        headers={
            "Origin": FRONTEND_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization, content-type, x-csrftoken",
        },
    )

    assert 200 <= reply.status < 300
    assert reply.headers.get("Access-Control-Allow-Origin") == FRONTEND_ORIGIN
    assert reply.headers.get("Access-Control-Allow-Credentials") == "true"
    assert {"authorization", "content-type", "x-csrftoken"} <= reply.header_values(
        "Access-Control-Allow-Headers"
    )
    assert "post" in reply.header_values("Access-Control-Allow-Methods")


def test_tc_sec_005_05_a_credentialed_request_from_an_unconfigured_origin_is_rejected(account):
    """TC-SEC-005-05 — A credentialed request from an unconfigured origin is rejected."""
    session = Session(UNCONFIGURED_ORIGIN)
    session.bootstrap_csrf()

    reply = session.call("POST", "/api/v1/auth/login/", account, csrf=True)

    assert reply.status == 403 and reply.json() == CSRF_FAILURE
    assert reply.headers.get("Access-Control-Allow-Origin") is None
    assert "refresh_token" not in reply.cookies
    assert reply.headers.get_all("Set-Cookie") is None


def test_tc_sec_005_06_a_valid_csrf_token_from_a_configured_origin_is_accepted(account):
    """TC-SEC-005-06 — A valid CSRF token from a configured origin is accepted."""
    session = Session(FRONTEND_ORIGIN)
    session.bootstrap_csrf()

    reply = session.call("POST", "/api/v1/auth/login/", account, csrf=True)

    assert reply.status == 200 and set(reply.json()) == {"access_token"}
    assert reply.headers.get("Access-Control-Allow-Origin") == FRONTEND_ORIGIN
    assert "refresh_token" in reply.cookies


def test_tc_sec_005_07_a_csrf_protected_request_from_an_unconfigured_origin_is_rejected():
    """TC-SEC-005-07 — A CSRF-protected request from an unconfigured origin is rejected."""
    session = Session(UNCONFIGURED_ORIGIN)
    session.bootstrap_csrf()

    # Logout is CSRF-protected and needs no account, so the Origin check alone decides.
    reply = session.call("POST", "/api/v1/auth/logout/", csrf=True)

    assert reply.status == 403 and reply.json() == CSRF_FAILURE


# ---- TECH-006: HTTPS only ---------------------------------------------------------


def test_tc_tech_006_01_public_frontend_and_backend_urls_use_https():
    """TC-TECH-006-01 — Public frontend and backend URLs use HTTPS."""
    assert BASE_URL.startswith("https://") and FRONTEND_ORIGIN.startswith("https://")

    health = send("GET", BASE_URL + "/api/v1/health/")
    assert health.status == 200 and health.json() == {"status": "ok"}

    frontend = send("GET", FRONTEND_ORIGIN + "/", headers={"Accept": "text/html"})
    assert frontend.status == 200 and b'<div id="root">' in frontend.body

    # A plain-HTTP request to the API is redirected to HTTPS rather than served.
    host = urlsplit(BASE_URL).hostname
    connection = http.client.HTTPConnection(host, 80, timeout=TIMEOUT)
    try:
        connection.request("GET", "/api/v1/health/")
        response = connection.getresponse()
        location = response.headers.get("Location", "")
    finally:
        connection.close()
    assert 300 <= response.status < 400
    assert location.startswith(f"https://{host}")


def test_tc_tech_006_02_normal_application_flows_do_not_require_plain_http():
    """TC-TECH-006-02 — Normal application flows do not require plain HTTP."""
    # The frontend loads its assets over HTTPS and was built against the HTTPS API.
    index = send("GET", FRONTEND_ORIGIN + "/", headers={"Accept": "text/html"})
    assert index.status == 200
    html = index.body.decode()
    assets = re.findall(r'(?:src|href)="([^"]+)"', html)
    assert assets and not [asset for asset in assets if asset.startswith("http:")]
    bundles = [asset for asset in assets if asset.endswith(".js")]
    assert bundles, "the page loads no script"
    bundle = send("GET", urljoin(FRONTEND_ORIGIN + "/", bundles[0]), headers={"Accept": "*/*"})
    assert bundle.status == 200 and BASE_URL.encode() in bundle.body

    # Register -> log in -> create an examination -> dashboard -> refresh -> log out,
    # every request over HTTPS (send() refuses anything else, including redirects).
    session = Session(FRONTEND_ORIGIN)
    email = f"deployment-flow-{int(time.time())}-{secrets.token_hex(3)}@example.com"
    password = secrets.token_urlsafe(18)
    reply = session.call(
        "POST",
        "/api/v1/auth/register/",
        {"email": email, "password": password, "timezone": TIMEZONE},
    )
    assert reply.status == 201

    csrf = session.bootstrap_csrf()
    assert csrf.cookies["csrftoken"]["secure"] is True
    login = session.call(
        "POST", "/api/v1/auth/login/", {"email": email, "password": password}, csrf=True
    )
    assert login.status == 200
    assert login.cookies["refresh_token"]["secure"] is True
    assert login.cookies["refresh_token"]["samesite"] == "None"
    session.access_token = login.json()["access_token"]

    scheduled = datetime.now(ZoneInfo(TIMEZONE)).date() + timedelta(days=30)
    created = session.call(
        "POST",
        "/api/v1/examinations/",
        {"title": "Deployment check", "status": "planned", "scheduled_date": str(scheduled)},
        bearer=True,
    )
    assert created.status == 201
    dashboard = session.call("GET", "/api/v1/dashboard/", bearer=True)
    assert dashboard.status == 200
    assert created.json()["id"] in [item["id"] for item in dashboard.json()["upcoming"]]

    refreshed = session.call("POST", "/api/v1/auth/refresh/", csrf=True)
    assert refreshed.status == 200
    assert refreshed.cookies["refresh_token"]["secure"] is True

    logged_out = session.call("POST", "/api/v1/auth/logout/", csrf=True)
    assert logged_out.status == 204
    assert logged_out.cookies["refresh_token"]["secure"] is True
