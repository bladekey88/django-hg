from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


from users.managers import CustomUserManager

# Create your models here.


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("Email Address"), unique=True)
    uid = models.CharField("User ID", max_length=20, unique=True)
    idnumber = models.CharField("ID Number", max_length=20, unique=True)
    is_staff = models.BooleanField("Is Staff", default=False)
    is_active = models.BooleanField("Is Active", default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True, default=None)
    first_name = models.CharField("First Name", max_length=255)
    middle_name = models.CharField("Middle Name", max_length=255, blank=True)
    last_name = models.CharField("Last Name", max_length=255)
    common_name = models.CharField("Preferred Name", max_length=255)

    USERNAME_FIELD = "uid"
    REQUIRED_FIELDS = ["email", "idnumber"]

    objects = CustomUserManager()

    def full_name(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}"

    def full_common_name(self):
        return f"{self.common_name} {self.middle_name} {self.last_name}"

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.idnumber} - {self.email}"


class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    GRYFFINDOR = "GR"
    HUFFLEPUFF = "HU"
    RAVENCLAW = "RA"
    SLYTHERIN = "SL"
    UNSORTED = "UN"
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

    class Year(models.IntegerChoices):
        UNKNOWN = 0
        FIRST = 1
        SECOND = 2
        THIRD = 3
        FOURTH = 4
        FIFTH = 5
        SIXTH = 6
        SEVENTH = 7

    year = models.IntegerField(
        choices=Year.choices,
        default=Year.UNKNOWN,
        validators=[
            MaxValueValidator(7),
            MinValueValidator(1),
        ],
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

    def is_owl_student(self):
        return self.year <= 5

    def is_newt_student(self):
        return self.year >= 6

    def __str__(self):
        return f"{self.user.idnumber} - {self.user.email} - {self.house} {self.year}"

    def __repr__(self):
        return self.user.email
