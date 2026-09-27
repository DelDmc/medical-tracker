from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header

from .models import User
from .tokens import TokenError, decode_access_token


class BearerAccessTokenAuthentication(BaseAuthentication):
    """`Authorization: Bearer <access_token>` (ADS-FR-005-04, ADS-FR-005-07).

    Only an unexpired HS256 token whose `token_type` is `access` authenticates; a
    refresh token presented here is rejected.
    """

    keyword = b"bearer"

    def authenticate(self, request):
        parts = get_authorization_header(request).split()
        if not parts or parts[0].lower() != self.keyword:
            return None
        if len(parts) != 2:
            raise exceptions.AuthenticationFailed("Invalid bearer authorization header.")
        try:
            payload = decode_access_token(parts[1].decode("ascii"))
        except (TokenError, UnicodeDecodeError):
            raise exceptions.AuthenticationFailed(
                "The access token is invalid or expired."
            ) from None
        try:
            user = User.objects.get(pk=int(payload["sub"]), is_active=True)
        except (User.DoesNotExist, ValueError):
            raise exceptions.AuthenticationFailed(
                "The access token is invalid or expired."
            ) from None
        return user, payload

    def authenticate_header(self, request):
        # Makes DRF answer unauthenticated requests with 401 rather than 403.
        return 'Bearer realm="api"'
