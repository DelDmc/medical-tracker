import importlib
import os
import sys
from unittest import mock

import pytest
from rest_framework.test import APIClient

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
