from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User
from .timezones import canonical_timezone

DUPLICATE_EMAIL = "An account with this email address already exists."
UNSUPPORTED_TIMEZONE = "Select a supported timezone."
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128


def password_field(**kwargs):
    """The password policy's length bounds (ADS-FR-003-01), shared by every password input."""
    return serializers.CharField(
        write_only=True,
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
        trim_whitespace=False,
        style={"input_type": "password"},
        **kwargs,
    )


def validate_new_password(password: str, user: User) -> None:
    """Run the ADS-SEC-003-01 validators, reporting failures as a `password`-style list."""
    try:
        password_validation.validate_password(password, user=user)
    except DjangoValidationError as error:
        raise serializers.ValidationError(list(error.messages)) from None


def validate_supported_timezone(value: str) -> str:
    try:
        return canonical_timezone(value)
    except ValueError:
        raise serializers.ValidationError(UNSUPPORTED_TIMEZONE) from None


class AccountSerializer(serializers.ModelSerializer):
    """The account representation: `id`, `email`, `timezone` (api_contract.md §6.1)."""

    class Meta:
        model = User
        fields = ["id", "email", "timezone"]
        read_only_fields = ["id", "email", "timezone"]


class AccountUpdateSerializer(serializers.ModelSerializer):
    """`PATCH /api/v1/account/`: only `timezone` is writable (api_contract.md §6.2)."""

    class Meta:
        model = User
        fields = ["id", "email", "timezone"]
        read_only_fields = ["id", "email"]

    def validate_timezone(self, value):
        return validate_supported_timezone(value)


class PasswordChangeSerializer(serializers.Serializer):
    """`POST /api/v1/account/password/` (ADS-FR-048-01).

    The current password must match the stored hash and the new one must pass the
    registration policy; if either check fails nothing is saved.
    """

    current_password = serializers.CharField(
        write_only=True, max_length=PASSWORD_MAX_LENGTH, trim_whitespace=False
    )
    new_password = password_field()

    def validate_current_password(self, value):
        if not self.context["request"].user.check_password(value):
            raise serializers.ValidationError("Your current password is incorrect.")
        return value

    def validate_new_password(self, value):
        validate_new_password(value, self.context["request"].user)
        return value

    def save(self):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        return user


class RegistrationSerializer(serializers.Serializer):
    """`POST /api/v1/auth/register/` (ADS-FR-001-01 … ADS-FR-004-01, ADS-SEC-003-01)."""

    email = serializers.EmailField(
        max_length=254,
        validators=[
            # Case-insensitive uniqueness (ADS-FR-002-01); the database constraint on
            # Lower(email) backs this up against concurrent registrations.
            UniqueValidator(queryset=User.objects.all(), lookup="iexact", message=DUPLICATE_EMAIL)
        ],
    )
    password = password_field()
    timezone = serializers.CharField(max_length=64)

    def validate_email(self, value):
        return User.objects.normalize_email(value)

    def validate_timezone(self, value):
        return validate_supported_timezone(value)

    def validate(self, attrs):
        candidate = User(email=attrs["email"], timezone=attrs["timezone"])
        try:
            validate_new_password(attrs["password"], candidate)
        except serializers.ValidationError as error:
            raise serializers.ValidationError({"password": error.detail}) from None
        return attrs

    def create(self, validated_data):
        try:
            with transaction.atomic():
                return User.objects.create_user(**validated_data)
        except IntegrityError:
            raise serializers.ValidationError({"email": [DUPLICATE_EMAIL]}) from None


class LoginSerializer(serializers.Serializer):
    """`POST /api/v1/auth/login/` input. Any credential mismatch is a generic 401."""

    email = serializers.CharField(max_length=254)
    password = serializers.CharField(max_length=PASSWORD_MAX_LENGTH, trim_whitespace=False)


class AccessTokenSerializer(serializers.Serializer):
    access_token = serializers.CharField()
