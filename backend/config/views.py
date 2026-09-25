from django.http import JsonResponse
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    """`GET /api/v1/health/` — ADS-TECH-004-01. Exposes no configuration or secret value."""

    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        auth=[],
        responses={200: inline_serializer("HealthResponse", {"status": serializers.CharField()})},
    )
    def get(self, request):
        return Response({"status": "ok"})


def not_found(request, exception=None):
    return JsonResponse({"detail": "Not found."}, status=404)


def server_error(request):
    return JsonResponse({"detail": "A server error occurred."}, status=500)
