from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.urls import reverse

from users.managers import CustomUserManager


# Create your models here.
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("Email Address"), unique=True)
    uid = models.CharField("User ID", max_length=20, unique=True)
    idnumber = models.CharField("ID Number", max_length=20, unique=True)
    is_staff = models.BooleanField("Access Managed Area", default=False)
    is_active = models.BooleanField("Is Active", default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True, default=None)
    first_name = models.CharField("First Name", max_length=255)
    middle_name = models.CharField("Middle Name", max_length=255, blank=True)
    last_name = models.CharField("Last Name", max_length=255)
    common_name = models.CharField("Preferred Name", max_length=255)

    class Sex(models.TextChoices):
        UNKNOWN = "U", "Unknown"
        MALE = "M", "Male"
        FEMALE = "F", "Female"

    sex = models.CharField(
        "Sex", max_length=1, choices=Sex.choices, default=Sex.UNKNOWN
    )

    USERNAME_FIELD = "uid"
    REQUIRED_FIELDS = ["email", "idnumber"]

    objects = CustomUserManager()

    class Title(models.TextChoices):
        UNKNOWN = "Unknown"
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

    title = models.CharField(
        "Title", max_length=20, default=Title.UNKNOWN, choices=Title.choices
    )

    created_externally = models.BooleanField(
        "Created From LDAP", default=False, editable=False
    )

    def full_name(self, include_middle=True, last_name_first=False):
        if include_middle:
            if last_name_first:
                return f" {self.last_name}, {self.first_name} {self.middle_name}"
            else:
                return f"{self.first_name} {self.middle_name} {self.last_name}"
        else:
            if last_name_first:
                return f"{self.last_name}, {self.first_name}"
            else:
                return f"{self.first_name} {self.last_name}"

    def full_common_name(self, include_middle=False, last_name_first=False):
        if include_middle:
            if last_name_first:
                return f"{self.last_name}, {self.common_name} {self.middle_name}"
            else:
                return f"{self.common_name} {self.middle_name} {self.last_name}"
        else:
            if last_name_first:
                return f"{self.last_name}, {self.common_name}"
            else:
                return f"{self.common_name} {self.last_name}"

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.full_name(True)} - {self.uid}"

    def __repr__(self):
        return f"{self.full_name(True)} - {self.uid}"

    def is_student(self):
        try:
            Student.objects.get(user=self)
            return True
        except Exception:
            return False

    def is_school_staff(self):
        try:
            Staff.objects.get(user=self)
            return True
        except Exception:
            return False

    def is_parent(self):
        try:
            Parent.objects.get(user=self)
            return True
        except Exception:
            return False


class Staff(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Staff Member"
        verbose_name_plural = "Staff Members"
        ordering = ("user__last_name",)

    class StaffType(models.TextChoices):
        ACADEMIC = "AC", "Academic"
        PASTORAL = "PA", "Pastoral"
        CLERICAL = "CL", "Clerical"
        OTHER = "OT", "Other"

    staff_type = models.TextField(
        max_length=2,
        choices=StaffType.choices,
    )

    is_head_of_house = models.BooleanField("Is Head of House", default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def clean(self, *args, **kwargs):
        USER_IS_STUDENT_ERROR = f"""
        {self.user.full_common_name()} cannot be a Staff Member because they
        already exist as a Student. If you wish to proceed you must remove
        the Student object."""

        student_exists = self.user.is_student()
        if student_exists:
            raise ValidationError(USER_IS_STUDENT_ERROR)
        else:
            print("Good to proceed")

    def __str__(self) -> str:
        return f"{self.user.full_name(True,True)} ({self.user.idnumber}-{self.get_staff_type_display()})"

    def __repr__(self) -> str:
        return f"{self.user.full_common_name()} ({self.user.idnumber})"


class SchoolHouse(models.Model):
    class Meta:
        verbose_name = "School House"
        verbose_name_plural = "School Houses"
        ordering = ["name"]

    name = models.CharField(
        "House Name",
        max_length=50,
        unique=True,
    )
    mascot = models.CharField(
        "House Mascot",
        max_length=50,
        unique=True,
    )
    ghost = models.CharField(
        "House Ghost",
        max_length=100,
        unique=True,
        null=True,
        blank=True,
    )
    crest = models.ImageField(
        "House Crest",
        null=True,
        blank=True,
    )
    # sorted_students = models.ForeignKey(
    #     Student,
    #     on_delete=models.PROTECT,
    #     null=True,
    #     blank=True,
    #     related_name="sorted_students",
    # )
    head_of_house = models.ForeignKey(
        Staff,
        on_delete=models.PROTECT,
        limit_choices_to={
            "staff_type": Staff.StaffType.ACADEMIC,
        },
        verbose_name="Professor",
    )

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"{self.name}"


class Student(models.Model):
    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        ordering = ("user__last_name",)
        permissions = [
            ("enrol_student", "Can sign up student to a course"),
        ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    class House(models.TextChoices):
        GRYFFINDOR = "GR", "Gryffindor"
        HUFFLEPUFF = "HU", "Hufflepuff"
        RAVENCLAW = "RA", "Ravenclaw"
        SLYTHERIN = "SL", "Slytherin"
        UNSORTED = "UN", "Unknown"

    house = models.CharField(
        max_length=2,
        default=House.UNSORTED,
        choices=House.choices,
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

    prefect = models.BooleanField("Is Prefect", default=False)
    test_house = models.ForeignKey(
        SchoolHouse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def is_sorted(self):
        return self.house in {
            self.House.GRYFFINDOR,
            self.House.HUFFLEPUFF,
            self.House.RAVENCLAW,
            self.House.SLYTHERIN,
        }

    def is_unsorted(self) -> bool:
        return self.house in {self.House.UNSORTED}

    def is_owl_student(self):
        return self.year <= 5

    def is_newt_student(self):
        return self.year >= 6

    def _validate_student_eligiblity(self):
        USER_IS_STAFF_ERROR = f"""
        {self.user.full_common_name()} cannot be a Student because they
        already exist as a Staff Member. If you wish to proceed you must remove
        the Staff object."""

        if self.user.is_school_staff():  # TODO add parent
            raise ValidationError(USER_IS_STAFF_ERROR)

    def _validate_prefect(self):
        USER_YEAR_INELIGBLE_PREFECT_ERROR = f"""
        {self.user.full_common_name()} cannot be assigned as a prefect as
        they are not a Fifth Year, Sixth, or Seventh Year."""
        USER_UNSORTED_INELIGBLE_PREFECT_ERROR = f"""
        {self.user.full_common_name()} cannot be assigned as a prefect as
        they have not been sorted into a House."""

        if self.year < 5 and self.prefect:
            raise ValidationError(USER_YEAR_INELIGBLE_PREFECT_ERROR)

        if self.house == self.House.UNSORTED and self.prefect:
            raise ValidationError(USER_UNSORTED_INELIGBLE_PREFECT_ERROR)

    def clean(self, *args, **kwargs):
        self._validate_student_eligiblity()
        self._validate_prefect()

    def __str__(self):
        return f"""{self.user.full_common_name(True,True)} ({self.user.idnumber}-{self.get_year_display()} Year {self.get_house_display()})"""

    def __repr__(self):
        return self.user.email

    def get_absolute_url(self):
        return reverse(
            "school:student_profile",
            kwargs={
                "student": self.user.uid,
            },
        )


class QuidditchPlayer(models.Model):
    class Meta:
        verbose_name = "Quidditch Player"
        verbose_name_plural = "Quidditch Players"
        ordering = [
            "student__house",
            "student__user__last_name",
            "student__user__first_name",
        ]

    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        unique=True,
    )
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

    def eligible_for_match(self):
        """
        Returns True if the player can play in matches.
        Any other return value is equivalent to False
        """

        if self.student.user.is_active:  # User inactive
            return (
                True
                if self.team_position
                and self.team_member_type
                and not self.is_suspended
                else False
            )
        else:
            return False

    def clean(self, *args, **kwargs):
        USER_IS_NOT_STUDENT_ERROR = f"""
        {self.student.user.full_common_name()} cannot be on a Quidditch Team
        because they are not a Student. If you wish to proceed you must assign
        the Student object to the User."""
        TOO_MANY_CAPTAINS_ERROR = f"""
        There are already four Quidditch Captains assigned, therefore this 
        Student cannot be saved as a Captain."""
        FIRST_YEAR_STUDENT_ERROR = f"""
        First Year Students are not permitted to play on Quidditch Teams"""

        try:
            student_exists = self.student
        except AttributeError:
            raise ValidationError(USER_IS_NOT_STUDENT_ERROR)

        if self.student.year < 2:
            raise ValidationError(FIRST_YEAR_STUDENT_ERROR)

        if self.is_captain:
            current_captains = QuidditchPlayer.objects.filter(is_captain=True)
            if current_captains.count() == 4 and self not in current_captains:
                raise ValidationError(TOO_MANY_CAPTAINS_ERROR)

        if student_exists:
            return super(QuidditchPlayer, self).save(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.clean()

    def __str__(self) -> str:
        return f"{self.student.user.common_name} {self.student.user.last_name}"

    def __repr__(self):
        return f"{self.student}: {self.team_member_type} {self.team_position}"


class Parent(models.Model):
    class Meta:
        verbose_name = "Parent"
        verbose_name_plural = "Parents"

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
    )
    children = models.ManyToManyField(
        Student,
        symmetrical=False,
        verbose_name="Children",
        related_name="children_of",
    )
    related_parent = models.ManyToManyField(
        "self",
        symmetrical=True,
        blank=True,
        default=None,
    )

    def get_children(self, raw=False):
        if raw:
            return [child for child in self.children.all().order_by("user__first_name")]
        else:
            return "\n\r| ".join(
                [
                    str(child.user.full_name())
                    for child in self.children.all().order_by("user__first_name")
                ]
            )

    def get_related_parent(self):
        return ",".join(
            [
                str(parent.user.full_name())
                for parent in self.related_parent.all().order_by("user__first_name")
            ]
        )

    def clean(self):
        student_exists = self.user.is_student()
        staff_exists = self.user.is_school_staff()
        if student_exists or staff_exists:
            USER_IS_STUDENT_OR_STAFF_ERROR = f"""
                {self.user.full_common_name()} cannot be added as a Parent
                because they already exist as a Student or Staff. If you
                wish to proceed you must remove the appropriate object:
                |Student: {student_exists}|
                |Staff_exists: {staff_exists}|"""
            raise ValidationError(USER_IS_STUDENT_OR_STAFF_ERROR)

    def __str__(self):
        return f"{self.user.full_name(True,True)} ({self.user.idnumber})"

    def __unicode__(self):
        return self.__str__()

    def __repr__(self):
        return self.user.uid
