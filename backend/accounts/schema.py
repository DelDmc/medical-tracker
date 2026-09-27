"""OpenAPI description of the bearer authentication class (ADS-TECH-001-01)."""

from drf_spectacular.extensions import OpenApiAuthenticationExtension


class BearerAccessTokenScheme(OpenApiAuthenticationExtension):
    target_class = "accounts.authentication.BearerAccessTokenAuthentication"
    name = "bearerAuth"

    def get_security_definition(self, auto_schema):
        return {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
