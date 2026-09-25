from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import AccountSerializer, RegistrationSerializer
from .throttles import RegisterRateThrottle


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
