"""Per-client-IP rate limits for the unauthenticated auth endpoints (ADS-SEC-007-01).

Rates are configured in `REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]`. A request over its
limit receives `429 Too Many Requests` with a `Retry-After` header.
"""

from rest_framework.throttling import SimpleRateThrottle

from config import clock


class ClientIPRateThrottle(SimpleRateThrottle):
    def get_cache_key(self, request, view):
        return self.cache_format % {"scope": self.scope, "ident": self.get_ident(request)}

    def timer(self):
        # Read time through the clock service so frozen-clock tests control the window.
        return clock.now().timestamp()


class RegisterRateThrottle(ClientIPRateThrottle):
    scope = "register"


class LoginRateThrottle(ClientIPRateThrottle):
    scope = "login"


class RefreshRateThrottle(ClientIPRateThrottle):
    scope = "refresh"
