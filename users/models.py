from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from users.managers import CustomUserManager

# Create your models here.


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("Email Address"), unique=True)
    idnumber = models.CharField("ID Number", max_length=20, unique=True)
    is_staff = models.BooleanField("Is Staff", default=False)
    is_active = models.BooleanField("Is Active", default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True, default=None)

    USERNAME_FIELD = "idnumber"
    REQUIRED_FIELDS = ["email"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.idnumber} - {self.email}"


class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField("First Name", max_length=255)
    middle_name = models.CharField("Middle Name", max_length=255, blank=True)
    last_name = models.CharField("Last Name", max_length=255)
    GRYFFINDOR = "GD"
    HUFFLEPUFF = "HP"
    RAVENCLAW = "RC"
    SLYTHERIN = "SR"
    UNSORTED = "US"
    HOUSE_CHOICES = [
        (GRYFFINDOR, "Gryffindor"),
        (HUFFLEPUFF, "Huffelpuff"),
        (RAVENCLAW, "Ravenclaw"),
        (SLYTHERIN, "Slytherin"),
        (UNSORTED, "Unsorted"),
    ]
    house = models.CharField(
        max_length=2,
        choices=HOUSE_CHOICES,
        default=UNSORTED,
    )

    def is_sorted(self) -> bool:
        return self.house in {
            self.GRYFFINDOR,
            self.HUFFLEPUFF,
            self.RAVENCLAW,
            self.SLYTHERIN,
        }

    def is_unsorted(self) -> bool:
        return self.house in {self.UNSORTED}
