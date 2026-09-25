from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView

from accounts.urls import account_patterns, auth_patterns
from config.views import HealthView

api_v1_patterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("auth/", include(auth_patterns)),
    path("account/", include(account_patterns)),
    # The generated OpenAPI contract (ADS-TECH-001-01); authenticated like every
    # endpoint outside the ADS-SEC-001-01 exemptions.
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
]

urlpatterns = [
    path("api/v1/", include(api_v1_patterns)),
]

handler404 = "config.views.not_found"
handler500 = "config.views.server_error"
