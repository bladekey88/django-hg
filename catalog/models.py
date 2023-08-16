from django.db import models
from django.urls import reverse
import uuid  # Required for unique book instances
from users.models import CustomUser
from datetime import date, datetime
from django.utils.timezone import utc
from math import ceil, floor


class Genre(models.Model):
    """Model representing a book genre."""

    class Meta:
        ordering = ["name"]

    name = models.CharField(
        max_length=200, help_text="Enter a book genre (e.g. Science Fiction)"
    )

    def __str__(self):
        """String for representing the Model object."""
        return self.name


class Book(models.Model):
    """Model representing a book (but not a specific copy of a book)."""

    class Meta:
        ordering = ["title"]

    title = models.CharField(max_length=200)

    # Foreign Key used because book can only have one author, but authors can have multiple books
    # Author is a string rather than an object because it hasn't been declared yet in the file
    author = models.ForeignKey("Author", on_delete=models.SET_NULL, null=True)

    summary = models.TextField(
        max_length=1000, help_text="Enter a brief description of the book"
    )
    isbn = models.CharField(
        "ISBN",
        max_length=13,
        unique=True,
        help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>',
    )

    # ManyToManyField used because genre can contain many books. Books can cover many genres.
    # Genre class has already been defined so we can specify the object above.
    genre = models.ManyToManyField(Genre, help_text="Select a genre for this book")

    def __str__(self):
        """String for representing the Model object."""
        return self.title

    def get_absolute_url(self):
        """Returns the URL to access a detail record for this book."""
        return reverse("catalog:book-detail", args=[str(self.id)])


class BookInstance(models.Model):
    """Model representing a specific copy of a book (i.e. that can be borrowed from the library)."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        help_text="Unique ID for this particular book across whole library",
    )
    book = models.ForeignKey("Book", on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True
    )

    LOAN_STATUS = (
        ("a", "Available"),
        ("l", "Lost"),
        ("m", "Maintenance"),
        ("o", "On loan"),
        ("r", "Reserved"),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default="m",
        help_text="Book availability",
    )

    class Meta:
        ordering = ["due_back"]
        permissions = (("can_mark_returned", "Set book as returned"),)

    def __str__(self):
        """String for representing the Model object."""
        return f"{self.id} ({self.book.title})"

    @property
    def is_overdue(self):
        """Determines if the book is overdue based on due date and current date."""
        return bool(self.due_back and date.today() > self.due_back)

    def can_be_checked_out(self):
        if self.status == "a":
            return True
        else:
            return False


class Author(models.Model):
    """Model representing an author."""

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField("Died", null=True, blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def get_absolute_url(self):
        """Returns the URL to access a particular author instance."""
        return reverse("catalog:author-detail", args=[str(self.id)])

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = f"{self.first_name} {self.last_name}"
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        """String for representing the Model object."""
        return f"{self.last_name}, {self.first_name}"


class Fine(models.Model):
    class Meta:
        verbose_name = "Fine"
        verbose_name_plural = "Fines"

    name = models.CharField("Fine Name", max_length=50, unique=True)
    value = models.FloatField("Fine Amount")

    class Frequency(models.TextChoices):
        HOURLY = ("H", "Hourly")
        DAILY = ("D", "Daily")
        WEEKLY = ("W", "Weekly")
        MONTHLY = ("M", "Monthly")
        ONE_OFF = ("O", "One-Offf")

    fine_frequency = models.CharField(
        "Fine Charge Frequency",
        choices=Frequency.choices,
        default="D",
        max_length=1,
    )

    def __str__(self):
        return f"{self.name}"

    def clean(self):
        self.value = round(self.value, 3)
        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Borrower(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    class BorrowerStatus(models.TextChoices):
        ACTIVE = ("A", "Active")
        SUSPENDED = ("S", "Suspended")
        PENDING = ("P", "Pending")
        INACTIVE = (("I", "Inactive"),)

    status = models.CharField(
        "Borrower Status",
        choices=BorrowerStatus.choices,
        default=BorrowerStatus.PENDING,
        max_length=17,
    )

    max_fine_amount = models.FloatField(
        "Fine Amount",
        blank=True,
        null=True,
        default=0.00,
    )

    borrow_limit = models.PositiveIntegerField(
        "Maximum Number of Items",
        blank=True,
        null=True,
        default=0,
    )

    fines = models.ManyToManyField(
        Fine,
        verbose_name="Fines",
        blank=True,
        through="BorrowerFine",
    )

    def __str__(self):
        return f"{self.user.full_name()}"


class BorrowerFine(models.Model):
    borrower = models.ForeignKey(Borrower, on_delete=models.PROTECT)
    fine = models.ForeignKey(Fine, on_delete=models.DO_NOTHING)
    item = models.ForeignKey(BookInstance, on_delete=models.DO_NOTHING)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    resolved_date = models.DateTimeField(blank=True, null=True, default=None)

    class Meta:
        verbose_name = "Borrower Fine"
        verbose_name_plural = "Borrower Fines"

    class FineStatus(models.TextChoices):
        OUTSTANDING = ("O", "Outstanding")
        PAID = ("P", "Paid")

    status = models.CharField(
        "Fine Status",
        choices=FineStatus.choices,
        max_length=11,
        default=FineStatus.OUTSTANDING,
    )

    def __str__(self) -> str:
        return f"{self.borrower} - {self.fine}"

    def current_fine_amount(self):
        return self.calculate_fine(self.fine.fine_frequency, rounded=False)

    def payable_fine_amount(self):
        return self.calculate_fine(self.fine.fine_frequency)

    def calculate_fine(self, frequency, rounded=True):
        if self.resolved_date:
            delta_seconds = self.resolved_date - self.created_date
        else:
            delta_seconds = datetime.now(tz=utc) - self.created_date
        value = self.fine.value

        if frequency == Fine.Frequency.ONE_OFF:
            return value
        elif frequency == Fine.Frequency.HOURLY:
            delta_hours = delta_seconds.total_seconds() / (60 * 60)
            if rounded:
                return ceil(delta_hours) * value
            else:
                return delta_hours * value
        elif frequency == Fine.Frequency.DAILY:
            delta_days = delta_seconds.total_seconds() / (60 * 60 * 24)
            if rounded:
                return ceil(delta_days) * value
            else:
                return delta_days * value
        elif frequency == Fine.Frequency.WEEKLY:
            delta_week = delta_seconds.total_seconds() / (60 * 60 * 24 * 7)
            if rounded:
                return ceil(delta_week) * value
            else:
                return (delta_week * value) + value
        elif frequency == Fine.Frequency.MONTHLY:
            delta_month = delta_seconds.total_seconds() / (60 * 60 * 24 * 30)
            if rounded:
                return ceil(delta_month) * value
            else:
                return (delta_month * value) + value

    def item_overdue_by(self):
        if self.resolved_date:
            delta_seconds = self.resolved_date - self.created_date
        elif self.created_date:
            delta_seconds = datetime.now(tz=utc) - self.created_date

        if self.fine.fine_frequency == Fine.Frequency.HOURLY:
            return f"""{ceil(delta_seconds.total_seconds()/ (60*60))} hours"""
        elif self.fine.fine_frequency == Fine.Frequency.DAILY:
            return f"{ceil(delta_seconds.total_seconds()/ (60*60*24))} days"
        elif self.fine.fine_frequency == Fine.Frequency.WEEKLY:
            return f"{ceil(delta_seconds.total_seconds()/ (60*60*24*7))} weeks"
        elif self.fine.fine_frequency == Fine.Frequency.MONTHLY:
            return f"{ceil(delta_seconds.total_seconds()/ (60*60*24*30))} months"

    def save(self, *args, **kwargs):
        if self.status == "P" and not self.resolved_date:
            self.resolved_date = datetime.now()
            super().save(*args, **kwargs)
        elif self.status == "P" and self.resolved_date:
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)
