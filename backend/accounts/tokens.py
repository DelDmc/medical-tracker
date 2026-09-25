"""JWT access and refresh tokens (D3; ADS-FR-005-06/07, ADS-FR-007-07/08/09/10).

Both token types are HS256 JWTs signed with `settings.JWT_SIGNING_KEY`
(ADS-SEC-004-01). Any other header `alg` is rejected before the signature is checked,
and each decoder accepts only its own `token_type`.

The refresh token's `exp` is always `session_start + 7 days`. `session_start` is fixed
at login and copied unchanged into every rotated token, and `issue_refresh_token`
requires it as an argument, so no code path can extend a session by rotating it.
"""

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt
from django.conf import settings

from config import clock

ALGORITHM = "HS256"
ACCESS = "access"
REFRESH = "refresh"
ACCESS_TOKEN_LIFETIME = timedelta(minutes=10)
REFRESH_SESSION_LIFETIME = timedelta(days=7)

_REQUIRED_CLAIMS = {
    ACCESS: ["sub", "token_type", "iat", "exp"],
    REFRESH: ["sub", "token_type", "jti", "session_start", "iat", "exp"],
}


class TokenError(Exception):
    """The token is malformed, forged, of the wrong type, or expired."""


@dataclass(frozen=True)
class IssuedToken:
    token: str
    payload: dict

    @property
    def expires_at(self) -> datetime:
        return datetime.fromtimestamp(self.payload["exp"], UTC)


def current_timestamp() -> int:
    return int(clock.now().timestamp())


def issue_access_token(user) -> IssuedToken:
    issued_at = current_timestamp()
    payload = {
        "sub": str(user.pk),
        "token_type": ACCESS,
        "iat": issued_at,
        "exp": issued_at + int(ACCESS_TOKEN_LIFETIME.total_seconds()),
    }
    return IssuedToken(_encode(payload), payload)


def issue_refresh_token(user, *, session_start: int) -> IssuedToken:
    """Issue a refresh token for the session that started at `session_start`.

    Login passes `current_timestamp()`; rotation passes the incoming token's own
    `session_start`. The expiry is computed only from `session_start`.
    """
    payload = {
        "sub": str(user.pk),
        "token_type": REFRESH,
        "jti": uuid.uuid4().hex,
        "session_start": session_start,
        "iat": current_timestamp(),
        "exp": session_start + int(REFRESH_SESSION_LIFETIME.total_seconds()),
    }
    return IssuedToken(_encode(payload), payload)


def decode_access_token(raw: str) -> dict:
    return _decode(raw, ACCESS)


def decode_refresh_token(raw: str) -> dict:
    payload = _decode(raw, REFRESH)
    if not isinstance(payload["session_start"], int):
        raise TokenError("The session start is malformed.")
    return payload


def _encode(payload: dict) -> str:
    return jwt.encode(payload, settings.JWT_SIGNING_KEY, algorithm=ALGORITHM)


def _decode(raw: str, token_type: str) -> dict:
    if not isinstance(raw, str) or not raw:
        raise TokenError("No token was supplied.")
    try:
        header = jwt.get_unverified_header(raw)
    except jwt.PyJWTError as error:
        raise TokenError("The token is malformed.") from error
    if header.get("alg") != ALGORITHM:
        raise TokenError("The token algorithm is not accepted.")
    try:
        payload = jwt.decode(
            raw,
            settings.JWT_SIGNING_KEY,
            algorithms=[ALGORITHM],
            # Expiry is checked below against the clock service, the backend's single
            # source of the current time.
            options={
                "require": _REQUIRED_CLAIMS[token_type],
                "verify_exp": False,
                "verify_iat": False,
                "verify_nbf": False,
            },
        )
    except jwt.PyJWTError as error:
        raise TokenError("The token is invalid.") from error
    if payload.get("token_type") != token_type:
        raise TokenError("The token is of the wrong type.")
    expires = payload["exp"]
    if not isinstance(expires, int) or current_timestamp() >= expires:
        raise TokenError("The token has expired.")
    return payload
