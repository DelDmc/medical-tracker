from django.contrib.auth import authenticate
from django.middleware.csrf import get_token
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from . import tokens
from .cookies import set_refresh_cookie
from .csrf import enforce_csrf
from .serializers import (
    AccessTokenSerializer,
    AccountSerializer,
    LoginSerializer,
    RegistrationSerializer,
)
from .throttles import LoginRateThrottle, RegisterRateThrottle

INVALID_CREDENTIALS = {"detail": "Invalid credentials."}


class RegisterView(APIView):
    """`POST /api/v1/auth/register/` — no bearer token, browser credentials, or CSRF."""

    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [RegisterRateThrottle]

    @extend_schema(auth=[], request=RegistrationSerializer, responses={201: AccountSerializer})
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(AccountSerializer(user).data, status=status.HTTP_201_CREATED)


class CsrfBootstrapView(APIView):
    """`GET /api/v1/auth/csrf/` — sets or renews the CSRF cookie and returns its token.

    The cookie is HttpOnly (ADS-SEC-005-07), so this response body is the only way the
    frontend obtains the token, which it then holds in memory (ADS-SEC-005-06).
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        auth=[],
        responses={200: inline_serializer("CsrfToken", {"csrf_token": serializers.CharField()})},
    )
    def get(self, request):
        return Response({"csrf_token": get_token(request._request)})


class LoginView(APIView):
    """`POST /api/v1/auth/login/` — CSRF-protected; no bearer token (ADS-FR-005-01…03).

    Success returns only `access_token` and sets the refresh token in its HttpOnly
    cookie. An unknown email and a wrong password get the identical 401
    (ADS-SEC-006-02).
    """

    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    @extend_schema(auth=[], request=LoginSerializer, responses={200: AccessTokenSerializer})
    def post(self, request):
        enforce_csrf(request)
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request._request,
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
        if user is None:
            return Response(INVALID_CREDENTIALS, status=status.HTTP_401_UNAUTHORIZED)

        access = tokens.issue_access_token(user)
        refresh = tokens.issue_refresh_token(user, session_start=tokens.current_timestamp())
        response = Response({"access_token": access.token})
        set_refresh_cookie(response, refresh)
        return response
