from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, idnumber, **extra_fields):
        """
        Create user with email, password and idnumber supplied by user
        """

        if not email:
            raise ValueError("Email must be provided.")
        if not idnumber:
            raise ValueError("ID Number must be provided")
        email = self.normalize_email(email)
        user = self.model(email=email, idnumber=idnumber, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, idnumber, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, idnumber, **extra_fields)
