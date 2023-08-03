from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.core.validators import MinLengthValidator
from users.models import Staff, Student

# Create your models here.


class BasicCourse(models.Model):
    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"
        ordering = [
            "course_code",
        ]

    name = models.CharField("Course Name", max_length=50, unique=True)
    description = models.TextField(
        "Description", max_length=2500, null=True, blank=True
    )
    course_code = models.CharField("Course Code", max_length=10, unique=True)

    class CourseType(models.TextChoices):
        OWL = (
            "OWL",
            "OWL",
        )
        NEWT = (
            "NEWT",
            "NEWT",
        )
        SPECIAL = (
            "SPECIAL",
            "Specialised Subject",
        )
        EXTERNAL = (
            "EXTERNAL",
            "External Course",
        )

    course_type = models.CharField(
        "Course Type",
        choices=CourseType.choices,
        default=CourseType.OWL,
        max_length=8,
    )

    class Required(models.TextChoices):
        REQUIRED = "R", "Required"
        ELECTIVE = "E", "Elective"

    required = models.CharField(
        "Course Category",
        choices=Required.choices,
        max_length=1,
        blank=True,
    )

    owner = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    slug = models.SlugField(
        null=False,
        unique=True,
    )

    def _validate_course_category(self):
        """The required field is only valid at OWL
        as any electives do not apply outside of that"""
        INVALID_CATEGORY_FOR_COURSE_TYPE_ERROR = (
            """The course category must not be set for non-OWL course types."""
        )
        OWL_COURSE_REQUIRED_CATEGORY_ERROR = (
            """OWL courses must have a Course Category."""
        )

        if self.course_type != self.CourseType.OWL and self.required:
            raise ValidationError(INVALID_CATEGORY_FOR_COURSE_TYPE_ERROR)
        elif self.course_type == self.CourseType.OWL and not self.required:
            raise ValidationError(OWL_COURSE_REQUIRED_CATEGORY_ERROR)

    def clean(self, *args, **kwargs):
        self._validate_course_category()
        if not self.slug:
            self.slug = self.course_code.lower()

    def __str__(self):
        return f"{self.name} ({self.course_code})"

    def __repr__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("school:course_detail", kwargs={"slug": self.slug})


class SchoolYear(models.Model):
    class Meta:
        verbose_name = "School Year"
        verbose_name_plural = "School Years"
        constraints = [
            models.UniqueConstraint(
                name="unique_year_period",
                fields=[
                    "start_year",
                    "end_year",
                ],
            )
        ]

    name = models.CharField("Name", max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    start_year = models.BigIntegerField(
        "Start Year",
        editable=False,
    )
    end_year = models.BigIntegerField(
        "End Year",
        editable=False,
    )
    slug = models.SlugField(
        null=False,
        unique=True,
    )

    def _validate_school_period_unique(self):
        """Check if year for start and end date combinationa are unique
        Check in clean method to separate out DB validation via constraint"""

        sy = self.start_date.year
        ey = self.end_date.year
        query = SchoolYear.objects.filter(start_year=sy, end_year=ey).exclude(
            id=self.id  # type: ignore
        )
        if query.exists():
            DEFINED_SCHOOL_YEAR_EXISTS_ERROR = f"""The defined school period
              ({sy}-{ey}) already exists under the name {query[0]}"""
            raise ValidationError(DEFINED_SCHOOL_YEAR_EXISTS_ERROR)

    def _validate_school_period_date(self):
        MAX_DAYS = 366
        MIN_DAYS = 364
        delta = self.end_date - self.start_date
        SCHOOL_YEAR_INVALID_LENGTH_ERROR = f"""
        Defined school year duration is not valid.
        The selected length is {delta.days} days.
        The minimum length is {MIN_DAYS} days.
        The maximum length is {MAX_DAYS} days.
        """
        if delta.days > MAX_DAYS or delta.days < MIN_DAYS:
            raise ValidationError(SCHOOL_YEAR_INVALID_LENGTH_ERROR)

    def get_two_year_format(self):
        return f"{str(self.start_year)[2:]}{str(self.end_year)[2:]}"

    def clean(self, *args, **kwargs):
        self._validate_school_period_date()
        self._validate_school_period_unique()

    def save(self, *args, **kwargs):
        self.clean()
        self.start_year = self.start_date.year
        self.end_year = self.end_date.year
        if not self.slug:
            self.slug = f"{str(self.start_year)[2:]}{str(self.end_year)[2:]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"

    def get_absolute_url(self):
        return reverse("school:schedule_detail", kwargs={"slug": self.slug})


class BasicClass(models.Model):
    class Meta:
        ordering = [
            "name",
        ]
        verbose_name = "Class"
        verbose_name_plural = "Classes"
        constraints = [
            models.UniqueConstraint(
                name="name_course",
                fields=[
                    "name",
                    "course",
                ],
            )
        ]

    name = models.CharField(
        "Class Name",
        max_length=100,
        unique=True,
        validators=[
            MinLengthValidator(3),
        ],
    )
    course = models.ForeignKey(BasicCourse, on_delete=models.PROTECT)
    school_year = models.ForeignKey(
        SchoolYear,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    teacher = models.ManyToManyField(
        Staff,
        limit_choices_to={
            "staff_type": Staff.StaffType.ACADEMIC,
        },
        verbose_name="Professor",
    )
    student = models.ManyToManyField(
        Student, verbose_name="student", blank=True, through="Enrolment"
    )
    class_code = models.CharField(
        "Class Code",
        max_length=20,
        editable=False,
        blank=True,
        null=True,
        unique=True,
    )

    slug = models.SlugField(
        null=False,
        unique=True,
    )

    def clean(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.class_code

    def save(self, *args, **kwargs):
        self.class_code = self.get_class_code()
        if not self.slug:
            self.slug = self.class_code.lower()
        super().save(*args, **kwargs)

    def get_class_code(self):
        return f"{self.name[:3].upper()}-{self.course.course_code}Y{self.school_year.get_two_year_format()}"

    def __str__(self):
        return f"{self.course.name} ({self.get_class_code()})"

    def __repr__(self):
        return f"{self.name} - {self.get_class_code()}"

    def get_absolute_url(self):
        return reverse(
            "school:class_detail",
            kwargs={
                "slug": self.course.slug,
                "class_slug": self.slug,
            },
        )

    def get_enrolable_subjects(self):
        year_ordinal = self.student.get_year_display()
        return BasicClass.objects.filter(name__icontains=year_ordinal)


class Enrolment(models.Model):
    class Meta:
        ordering = [
            "student__user__last_name",
        ]
        verbose_name = "Enrolment"
        verbose_name_plural = "Enrolments"
        constraints = [
            models.UniqueConstraint(
                name="unique_student_class",
                fields=[
                    "student",
                    "basic_class",
                ],
            )
        ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    basic_class = models.ForeignKey(BasicClass, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class ClassStatus(models.TextChoices):
        ACTIVE = "A", "Active"
        EXPIRED = "E", "Expired"
        NOT_ELIGIBLE = "N", "Not Eligible"
        PENDING = "P", "Pending"
        SUSPENDED = "S", "Suspended"

    student_class_status = models.CharField(
        "Status",
        max_length=1,
        blank=False,
        choices=ClassStatus.choices,
    )

    def __str__(self):
        return f"{self.student.user.uid} - {self.basic_class.name}"
