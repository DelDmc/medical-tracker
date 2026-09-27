from django.contrib.auth import authenticate
from django.db import IntegrityError, transaction
from django.middleware.csrf import get_token
from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import generics, serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from config.schema import (
    CSRF_FAILURE,
    ERROR_DETAIL,
    RETRY_AFTER,
    THROTTLED,
    UNAUTHENTICATED,
    VALIDATION_FAILURE,
)

from . import tokens
from .cookies import REFRESH_COOKIE_NAME, clear_refresh_cookie, set_refresh_cookie
from .csrf import enforce_csrf
from .models import RevokedRefreshToken, User, revoke_refresh_token
from .serializers import (
    AccessTokenSerializer,
    AccountSerializer,
    AccountUpdateSerializer,
    LoginSerializer,
    PasswordChangeSerializer,
    RegistrationSerializer,
)
from .throttles import LoginRateThrottle, RefreshRateThrottle, RegisterRateThrottle

INVALID_CREDENTIALS = {"detail": "Invalid credentials."}
INVALID_REFRESH_TOKEN = {"detail": "Refresh token is invalid or expired."}

INVALID_CREDENTIALS_RESPONSE = OpenApiResponse(
    ERROR_DETAIL,
    description="Invalid credentials: the same response for an unknown email and a "
    "wrong password (api_contract.md §5.4).",
)
INVALID_REFRESH_TOKEN_RESPONSE = OpenApiResponse(
    ERROR_DETAIL,
    description="The refresh token is expired, revoked, malformed, missing or "
    "otherwise invalid; the cookie is cleared (api_contract.md §5.5).",
)


class RegisterView(APIView):
    """`POST /api/v1/auth/register/` — no bearer token, browser credentials, or CSRF."""

    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [RegisterRateThrottle]

    @extend_schema(
        auth=[],
        request=RegistrationSerializer,
        parameters=[RETRY_AFTER],
        responses={201: AccountSerializer, 400: VALIDATION_FAILURE, 429: THROTTLED},
    )
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

    @extend_schema(
        auth=[],
        request=LoginSerializer,
        parameters=[RETRY_AFTER],
        responses={
            200: AccessTokenSerializer,
            400: VALIDATION_FAILURE,
            401: INVALID_CREDENTIALS_RESPONSE,
            403: CSRF_FAILURE,
            429: THROTTLED,
        },
    )
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


class RefreshView(APIView):
    """`POST /api/v1/auth/refresh/` — rotate the refresh token (ADS-FR-007-01…10).

    The token is read only from the `refresh_token` cookie; there is no JSON body. On
    success the submitted token is revoked and replaced by one carrying the same
    `session_start` (so the seven-day session is never extended). Every invalid,
    expired, revoked, malformed or missing token gets the same 401, no credentials,
    and a cleared cookie.
    """

    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [RefreshRateThrottle]

    @extend_schema(
        auth=[],
        request=None,
        parameters=[RETRY_AFTER],
        responses={
            200: AccessTokenSerializer,
            401: INVALID_REFRESH_TOKEN_RESPONSE,
            403: CSRF_FAILURE,
            429: THROTTLED,
        },
    )
    def post(self, request):
        enforce_csrf(request)
        try:
            payload = tokens.decode_refresh_token(request.COOKIES.get(REFRESH_COOKIE_NAME))
            user = User.objects.get(pk=int(payload["sub"]), is_active=True)
            with transaction.atomic():
                # Inserting the jti is the revocation check itself: a token already
                # revoked (or being rotated concurrently) violates the unique jti.
                RevokedRefreshToken.objects.create(
                    jti=payload["jti"], expires_at=tokens.IssuedToken("", payload).expires_at
                )
                replacement = tokens.issue_refresh_token(
                    user, session_start=payload["session_start"]
                )
        except (tokens.TokenError, User.DoesNotExist, ValueError, IntegrityError):
            response = Response(INVALID_REFRESH_TOKEN, status=status.HTTP_401_UNAUTHORIZED)
            clear_refresh_cookie(response)
            return response

        response = Response({"access_token": tokens.issue_access_token(user).token})
        set_refresh_cookie(response, replacement)
        return response


class LogoutView(APIView):
    """`POST /api/v1/auth/logout/` — CSRF-protected; reads the refresh cookie if present.

    A valid refresh token is revoked (ADS-FR-006-02). Whatever the token's state —
    valid, expired, revoked, invalid or missing — the response is the same empty 204
    and the cookie is cleared (ADS-FR-006-03, ADS-FR-006-04). Access tokens already
    issued stay valid until their own expiry (ADS-FR-006-09).
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(auth=[], request=None, responses={204: None, 403: CSRF_FAILURE})
    def post(self, request):
        enforce_csrf(request)
        try:
            payload = tokens.decode_refresh_token(request.COOKIES.get(REFRESH_COOKIE_NAME))
        except tokens.TokenError:
            payload = None
        if payload is not None:
            revoke_refresh_token(payload)

        response = Response(status=status.HTTP_204_NO_CONTENT)
        clear_refresh_cookie(response)
        return response


class AccountView(generics.RetrieveUpdateAPIView):
    """`GET` / `PATCH /api/v1/account/` — always the authenticated user's own account.

    There is no identifier in the path, so no other account can be addressed
    (ADS-FR-009-01). Changing the timezone leaves stored instants untouched.
    """

    serializer_class = AccountUpdateSerializer
    http_method_names = ["get", "patch", "head", "options"]

    def get_object(self):
        return self.request.user

    @extend_schema(responses={200: AccountSerializer, 401: UNAUTHENTICATED})
    def get(self, request, *args, **kwargs):
        return Response(AccountSerializer(request.user).data)

    @extend_schema(
        request=AccountUpdateSerializer,
        responses={200: AccountSerializer, 400: VALIDATION_FAILURE, 401: UNAUTHENTICATED},
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class PasswordChangeView(APIView):
    """`POST /api/v1/account/password/` — bearer-authenticated, no CSRF (ADS-FR-048-01).

    Success is `200 OK` with an empty body; neither password is ever returned.
    """

    @extend_schema(
        request=PasswordChangeSerializer,
        responses={200: None, 400: VALIDATION_FAILURE, 401: UNAUTHENTICATED},
    )
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)
