"""OpenAPI descriptions of the common error responses (api_contract.md §3).

Each view lists the error responses its api_contract.md section documents, so
`openapi.yaml` carries every documented status code rather than only the success one
(ADS-TECH-001-01).
"""

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, inline_serializer
from rest_framework import serializers

ERROR_DETAIL = inline_serializer("ErrorDetail", {"detail": serializers.CharField()})

UNAUTHENTICATED = OpenApiResponse(
    ERROR_DETAIL, description="Authentication failure (api_contract.md §3.1)."
)
CSRF_FAILURE = OpenApiResponse(
    ERROR_DETAIL,
    description="CSRF failure (api_contract.md §3.2): `X-CSRFToken` is missing or does not "
    "match the CSRF cookie. No credentials are issued.",
)
NOT_FOUND = OpenApiResponse(
    ERROR_DETAIL,
    description="Not found (api_contract.md §3.3): the record does not exist or belongs to "
    "another user.",
)
VALIDATION_FAILURE = OpenApiResponse(
    {"type": "object", "additionalProperties": {"type": "array", "items": {"type": "string"}}},
    description="Validation failure (api_contract.md §3.4): each field name, or "
    "`non_field_errors`, maps to its messages.",
)
THROTTLED = OpenApiResponse(ERROR_DETAIL, description="Rate limit exceeded (api_contract.md §3.5).")
RETRY_AFTER = OpenApiParameter(
    "Retry-After",
    OpenApiTypes.INT,
    OpenApiParameter.HEADER,
    response=[429],
    description="Seconds until the rate-limit window resets.",
)
