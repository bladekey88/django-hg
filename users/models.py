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

    class Title(models.TextChoices):
        MISS = "Miss"
        MR = "Mr"
        MRS = "Mrs"
        MS = "Ms"
        MX = "Mx"
        DR = "Doctor"
        MADAM = "Madam"
        MADAME = "Madame"
        MASTER = "Master"
        PROFESSOR = "Professor"
        MINISTER = "Minister"
        SIR = "Sir"
        DAME = "Dame"
        UNKNOWN = "Unknown"

    title = models.CharField(
        "Title", max_length=20, default=Title.UNKNOWN, choices=Title.choices
    )

    def full_name(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}"

    def full_common_name(self, include_middle=False):
        if include_middle:
            return f"{self.common_name} {self.middle_name} {self.last_name}"
        else:
            return f"{self.common_name} {self.last_name}"

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.idnumber} - {self.uid}"

    def is_student(self):
        try:
            Student.objects.get(user=self)
            return True
        except Exception:
            return False


class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    class House(models.TextChoices):
        GRYFFINDOR = "GR", "Gryffindor"
        HUFFLEPUFF = "HU", "Hufflepuff"
        RAVENCLAW = "RA", "Ravenclaw"
        SLYTHERIN = "SL", "Slytherin"
        UNSORTED = "UN", "Unknown"

    house = models.CharField(
        max_length=2,
        choices=House.choices,
        default=House.UNSORTED,
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

    class meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        ordering = ("user__last_name",)

    def is_sorted(self) -> bool:
        return self.house in {
            House.GRYFFINDOR,
            House.HUFFLEPUFF,
            House.RAVENCLAW,
            House.SLYTHERIN,
        }

    def is_unsorted(self) -> bool:
        return self.house in {House.UNSORTED}

    def is_owl_student(self):
        return self.year <= 5

    def is_newt_student(self):
        return self.year >= 6

    def __str__(self):
        return f"{self.user.full_common_name()} ({self.user.idnumber} {self.get_year_display()} Year {self.get_house_display()})"

    def __repr__(self):
        return self.user.email


class QuidditchPlayer(models.Model):
    class Meta:
        verbose_name = "Quidditch Player"
        verbose_name_plural = "Quidditch Players"
        ordering = ["student__house", "student__user__last_name"]

    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    is_captain = models.BooleanField("Is Captain", default=False)
    is_suspended = models.BooleanField("Is Suspended", default=False)

    class QuidditchTeamMeber(models.TextChoices):
        MEMBER = "ME", "Team Member"
        RESERVE = "RE", "Team Reserve"

    team_member_type = models.TextField(
        max_length=2,
        choices=QuidditchTeamMeber.choices,
    )

    class QuidditchPosition(models.TextChoices):
        KEEPER = "KE", "Keeper"
        CHASER = "CH", "Chaser"
        BEATER = "BE", "Beater"
        SEEKER = "SE", "Seeker"

    team_position = models.TextField(
        max_length=2,
        choices=QuidditchPosition.choices,
    )

    def __str__(self) -> str:
        return f"{self.student.user.common_name} {self.student.user.last_name} "

    def __repr__(self):
        return f"{self.student}: {self.team_member_type} {self.team_position}"
