from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.db.models.functions import Lower


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password, timezone, **extra_fields):
        """Create an account; the password only ever passes through `set_password`."""
        if not email or not str(email).strip():
            raise ValueError("An email address is required.")
        user = self.model(
            email=self.normalize_email(str(email).strip()), timezone=timezone, **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def get_by_natural_key(self, username):
        # Email addresses are unique case-insensitively, so they are looked up that way.
        return self.get(**{f"{self.model.USERNAME_FIELD}__iexact": username})


class User(AbstractBaseUser):
    """An application account (domain_model.md §3.1)."""

    email = models.EmailField(max_length=254, unique=True)
    timezone = models.CharField(max_length=64)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["timezone"]

    class Meta:
        constraints = [
            models.UniqueConstraint(Lower("email"), name="accounts_user_email_ci_unique"),
        ]

    def __str__(self):
        return self.email
