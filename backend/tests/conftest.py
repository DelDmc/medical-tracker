import importlib
import os
import sys
from unittest import mock

import pytest
from django.core.cache import cache
from rest_framework.test import APIClient

DEFAULT_PASSWORD = "correct-horse-battery"  # pragma: allowlist secret

SETTINGS_PACKAGE = "config.settings"
BASE_MODULE = f"{SETTINGS_PACKAGE}.base"


def load_settings_module(module_name: str, environ: dict[str, str]):
    """Import a settings module afresh against exactly `environ`.

    The modules Django already loaded stay untouched: the fresh copies are removed from
    `sys.modules` again afterwards, so the running test configuration is unaffected.
    """
    package = importlib.import_module(SETTINGS_PACKAGE)
    names = (BASE_MODULE, module_name)
    saved_modules = {name: sys.modules.pop(name) for name in names if name in sys.modules}
    saved_attrs = {
        attr: getattr(package, attr)
        for attr in (name.rsplit(".", 1)[1] for name in names)
        if hasattr(package, attr)
    }
    try:
        with mock.patch.dict(os.environ, environ, clear=True):
            return importlib.import_module(module_name)
    finally:
        for name in names:
            sys.modules.pop(name, None)
        sys.modules.update(saved_modules)
        for attr, value in saved_attrs.items():
            setattr(package, attr, value)


@pytest.fixture
def settings_env():
    """Load a named settings module against a supplied environment dict."""
    return load_settings_module


@pytest.fixture
def api_client():
    """An API client that enforces CSRF exactly as a browser request would experience it."""
    return APIClient(enforce_csrf_checks=True)


@pytest.fixture(autouse=True)
def reset_rate_limits():
    """Per-IP throttle counters live in the cache; clear them around every test (R7)."""
    cache.clear()
    yield
    cache.clear()


@pytest.fixture(autouse=True)
def fast_password_hashing(settings):
    """Hash with a fast algorithm in tests. TC-SEC-003-01 restores the real hasher."""
    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


@pytest.fixture
def make_user(db):
    from accounts.models import User

    created = iter(range(1, 10_000))

    def factory(email=None, password=DEFAULT_PASSWORD, timezone="Europe/Warsaw"):
        email = email or f"user{next(created)}@example.com"
        return User.objects.create_user(email=email, password=password, timezone=timezone)

    return factory


class BearerClient(APIClient):
    """An API client authenticated as `user`, with a token issued at request time.

    Issuing per request keeps the token valid however a test moves the frozen clock.
    """

    def __init__(self, user, **kwargs):
        super().__init__(**kwargs)
        self.user = user

    def request(self, **kwargs):
        from accounts.tokens import issue_access_token

        kwargs["HTTP_AUTHORIZATION"] = f"Bearer {issue_access_token(self.user).token}"
        return super().request(**kwargs)


@pytest.fixture
def client_for():
    return BearerClient


@pytest.fixture
def owner(make_user):
    return make_user(email="owner@example.com", timezone="Europe/Warsaw")


@pytest.fixture
def owner_client(owner):
    return BearerClient(owner)
