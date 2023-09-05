from django.db import models
from django.core.exceptions import ValidationError
import uuid
from users.models import CustomUser
from django.urls import reverse
from django.core.validators import MinValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType


# Create your models here.
class Language(models.Model):
    """
    List of languages by iso code (2 letter only because country code
    is not needed.
    This should be popluated by getting data from django.conf.locale.LANG_INFO
    """

    name = models.CharField(
        max_length=256,
        null=False,
        blank=False,
        verbose_name="Language name",
    )
    name_local = models.CharField(
        max_length=256,
        null=False,
        blank=True,
        default="",
        verbose_name="Language name (in that language)",
    )
    isocode = models.CharField(
        max_length=2,
        null=False,
        blank=False,
        unique=True,
        verbose_name="ISO 639-1 Language code",
        help_text="2 character language code without country",
    )
    sorting = models.PositiveIntegerField(
        blank=False,
        null=False,
        default=0,
        verbose_name="Sort Order",
        help_text="Increase to show at top of the list",
    )

    def __str__(self):
        return f"{self.name} ({self.isocode})"

    class Meta:
        verbose_name = "language"
        verbose_name_plural = "languages"
        ordering = (
            "-sorting",
            "name",
            "isocode",
        )


class Genre(models.Model):
    """Model representing a book genre."""

    name = models.CharField(
        "Name",
        max_length=200,
        help_text="Enter a book genre (e.g. Science Fiction)",
        unique=True,
    )

    class GenreObject(models.TextChoices):
        BOOK = ("B", "Book")
        VIDEOGAME = ("V", "Video Game")
        DVD = ("D", "DVD")
        BLURAY = ("BR", "Blu-Ray")

    class GenreType(models.TextChoices):
        FICTION = ("F", "Fiction")
        NONFICTION = ("NF", "Non-Fiction")

    genre_object = models.CharField(
        "Object",
        max_length=10,
        choices=GenreObject.choices,
        help_text="Choose the object type to which the genre applies",
    )

    genre_type = models.CharField(
        max_length=10,
        choices=GenreType.choices,
        help_text="Choose Genre Type",
        verbose_name="Type",
        null=True,
        blank=True,
    )

    def clean(self, *args, **kwargs):
        if self.genre_object == self.GenreObject.BOOK and not self.genre_type:
            raise ValidationError("A genre type must be set for Book genres.")
        elif self.genre_object != self.GenreObject.BOOK and self.genre_type:
            raise ValidationError("Genre type can only be set for Books")

        super().clean(*args, **kwargs)

    def __str__(self):
        """String for representing the Model object."""
        return f"{self.name}"  # type: ignore

    def __repr__(self):
        return f"{self.name}-{self.get_genre_object_display()}"  # type:ignore

    class Meta:
        ordering = ["name"]
        verbose_name = "Genre"
        verbose_name_plural = "Genres"


class Author(models.Model):
    """Model representing an author."""

    first_name = models.CharField(
        "First Name",
        max_length=100,
        null=True,
        blank=True,
    )
    middle_name = models.CharField(
        "Middle Name",
        max_length=100,
        null=True,
        blank=True,
    )
    last_name = models.CharField("Last Name", max_length=100)
    display_name = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField("Born", null=True, blank=True)
    date_of_death = models.DateField("Died", null=True, blank=True)

    class AuthorType(models.TextChoices):
        INDIVIDUAL = ("I", "Individual")
        GROUP = ("G", "Group")
        COMPANY = ("C", "Company")

    author_type = models.CharField(
        "Author Type",
        max_length=10,
        choices=AuthorType.choices,
        default=AuthorType.INDIVIDUAL,
        blank=True,
    )

    class Meta:
        ordering = ["display_name"]
        verbose_name = "Author"
        verbose_name_plural = "Authors"

    def get_absolute_url(self):
        """Returns the URL to access a particular author instance."""
        return reverse("library:author-detail", args=[str(self.id)])  # type: ignore # noqa

    def save(self, *args, **kwargs):
        if not self.display_name:
            if self.middle_name:
                self.display_name = (
                    f"{self.first_name} {self.middle_name} {self.last_name}"
                )
            else:
                self.display_name = f"{self.first_name} {self.last_name}"
        self.clean()  # type: ignore
        super().save(*args, **kwargs)

    def __str__(self):
        """String for representing the Model object."""
        return f"{self.display_name}"

    def __repr__(self):
        return f"{self.last_name}. {self.first_name} {self.middle_name}"


class Series(models.Model):
    title = models.CharField("Series Name", max_length=200, unique=True)
    summary = models.TextField(
        max_length=1000,
        help_text="Enter a brief description of the item",
    )
    genre = models.ManyToManyField(
        Genre,
        help_text="Select a genre for this item",
    )

    author = models.ManyToManyField(Author)
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        help_text="Unique ID for this particular item across whole library",
    )

    publish_date = models.DateField(
        "Published On",
        blank=True,
        null=True,
    )

    series_size = models.PositiveIntegerField(
        "Number of Items in Series",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Series"
        verbose_name_plural = "Series"
        ordering = ["title"]

    def number_items_in_series(self):
        return self.book_set.all().count() + self.videogame_set.all().count()

    def __str__(self):
        return f"{self.title}"

    def __repr__(self):
        return f"{self.title}"

    def get_absolute_url(self):
        """Returns the URL to access a particular series instance."""
        return reverse("library:series-detail", args=[str(self.id)])  # type: ignore # noqa


class LibraryItem(models.Model):
    """Abstract Model representing a generic item but not any specific copy"""

    title = models.CharField(
        "title",
        max_length=200,
        help_text="Enter the name/title for this item",
    )
    summary = models.TextField(
        max_length=1000,
        help_text="Enter a brief description of the item",
    )
    genre = models.ManyToManyField(
        Genre,
        help_text="Select a genre for this item",
    )

    author = models.ManyToManyField(Author)

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        help_text="Unique ID for this particular item across whole library",
        editable=False,
    )

    publish_date = models.DateField(
        "First Published On",
        blank=True,
        null=True,
    )
    part_of_series = models.BooleanField(
        "Part of Series",
        default=False,
        blank=True,
        null=True,
    )

    series = models.ForeignKey(
        Series,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    position_in_series = models.IntegerField(
        "Number in Series",
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["title"]
        verbose_name = "Library Item"
        verbose_name_plural = "Library Items"
        abstract = True

    class ItemType(models.TextChoices):
        BOOK = ("B", "Book")
        DIGITAL = ("D", "Digital")
        CD = ("CD", "Compact Disc")
        VIDEOGAME = ("V", "Video Game")

    item_type = models.CharField(
        "Item Type",
        max_length=7,
        choices=ItemType.choices,
        editable=False,
    )
    item_language = models.ManyToManyField(
        Language,
        "Language",
    )
    visible = models.BooleanField("Item Visible", default=True)
    restricted = models.BooleanField("Item Restricted", default=False)

    def __str__(self):
        return f"{self.title}"

    def get_absolute_url(self):
        """Returns the URL to access a detail record for this item."""
        raise NotImplementedError(
            f"'get_absolute_url' method must be implemented in '{self._meta}'"
        )

    def get_count_child_instance(self):
        """Get the count of the instance objects of the model"""
        raise NotImplementedError(
            f"'get_count_child_instance' method must be implemented in '{self._meta}'"
        )

    def save(self):
        self.get_count_child_instance()
        super().save()


class Book(LibraryItem):
    item_type = models.CharField(
        "Type",
        max_length=7,
        default="B",
        editable=False,
    )

    isbn = models.CharField(
        "ISBN",
        max_length=13,
        unique=True,
        help_text="""13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>""",  # noqa
    )

    genre = models.ManyToManyField(
        Genre,
        help_text="Select a genre for this item",
        limit_choices_to={"genre_object": "B"},
    )

    item_language = models.ManyToManyField(
        Language,
        related_name="book_language",
        default="English",
    )

    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"
        ordering = ["series", "position_in_series", "title"]

    def get_absolute_url(self):
        """Returns the URL to access a detail record for this book."""
        return reverse("library:book-detail", args=[str(self.id)])

    def get_count_child_instance(self):
        return self.bookinstance_set.all().count()

    def get_available_child_instance(self):
        return self.bookinstance_set.filter(
            status=BookInstance.BookItemStatus.AVAILABLE
        ).count()


class VideoGame(LibraryItem):
    item_type = models.CharField(
        "Type",
        max_length=15,
        default="V",
        editable=False,
    )

    genre = models.ManyToManyField(
        Genre,
        help_text="Select a genre for this item",
        limit_choices_to={"genre_object": "V"},
    )

    author = models.ManyToManyField(
        Author,
        verbose_name="publisher",
        limit_choices_to={"author_type": "C"},
        related_name="publisher",
    )
    developer = models.ManyToManyField(
        Author,
        verbose_name="developer",
        limit_choices_to={"author_type": "C"},
        related_name="developer",
    )

    class SystemPlatform(models.TextChoices):
        PC = ("PC", "PC")
        NES = ("NES", "Nintendo Enetertainment System")
        SNES = ("SNES", "Super Nintendo Entertainment System")
        N64 = ("N64", "Nintendo 64")
        GC = ("GC", "Nintendo Gamecube")
        WII = ("WII", "Nintendo Wii")
        WIIU = ("WIIU", "Wii-U")
        SWITCH = ("SWITCH", "Nintendo Switch")
        GB = ("GB", "Gameboy")
        GBC = ("GBC", "Gameboy Color")
        GBA = ("GBA", "Gameboy Advance")
        DS = ("DS", "Nintendo DS")
        THREEDS = ("3DS", "3DS")
        PS1 = ("PS1", "Playstation 1")
        PS2 = ("PS2", "Playstation 2")
        PS3 = ("PS3", "Playstation 3")
        PS4 = ("PS4", "Playstation 4")
        PS5 = ("PS5", "Playstation 5")
        XBOX = ("XBOX", "XBox")
        X360 = ("X360", "XBox 360")
        XONE = ("XONE", "XBox One")
        XSXS = ("XSXSE", "XBox Series X/S")

    platform = models.CharField(
        "Platform",
        max_length=10,
        choices=SystemPlatform.choices,
    )

    item_language = models.ManyToManyField(
        Language,
        related_name="videogame_language",
        default="English",
    )

    def get_absolute_url(self):
        """Returns the URL to access a detail record for this videogame."""
        return reverse("library:videogame-detail", args=[str(self.id)])

    class Meta:
        verbose_name = "Video Game"
        verbose_name_plural = "Video Games"
        ordering = ["series", "position_in_series", "title"]


class Borrower(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="library_user",
        verbose_name="Member",
    )

    class Meta:
        verbose_name = "Borrower"
        verbose_name_plural = "Borrowers"
        ordering = [
            "user__last_name",
            "user__first_name",
        ]

    class BorrowerStatus(models.TextChoices):
        ACTIVE = ("A", "Active")
        SUSPENDED = ("S", "Suspended")
        PENDING = ("P", "Pending")
        INACTIVE = ("I", "Inactive")

    status = models.CharField(
        "Borrower Status",
        choices=BorrowerStatus.choices,
        default=BorrowerStatus.PENDING,
        max_length=17,
    )

    max_fine_amount = models.FloatField(
        "Maximum Fine Amount",
        validators=[
            MinValueValidator(0.0, "Amount must be a positive number"),
        ],
        blank=True,
        null=True,
        default=5.00,
        help_text="Maximum fine before revoking borrowing privileges",
    )

    borrow_limit = models.PositiveIntegerField(
        "Maximum Number of Items",
        blank=True,
        null=True,
        default=5,
        help_text="Maximum number of items a user can borrow at any one time",
    )

    def __str__(self):
        return f"{self.user.full_name()}"

    def get_absolute_url(self):
        return reverse("library:borrower-detail", kwargs={"pk": self.pk})

    @property
    def is_librarian(self):
        return self.user.groups.filter(name="Librarians").exists()


class BookInstance(models.Model):
    instance_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        help_text="Unique ID for this particular book instance across whole library",
        editable=False,
    )
    book = models.ForeignKey("Book", on_delete=models.RESTRICT, null=True)

    class BookItemStatus(models.TextChoices):
        AVAILABLE = ("A", "Available")
        DAMAGED = ("D", "Damaged")
        INTERNAL = ("I", "Internal")
        LOST = ("L", "Lost")
        ON_HOLD = ("H", "On Hold")
        ON_LOAN = ("O", "On Loan")
        MISSING = ("M", "Missing")
        PROCESSING = ("P", "Processing")
        UNAVAILABLE = ("U", "Unavailable")

    status = models.TextField(
        "Status",
        choices=BookItemStatus.choices,
        default=BookItemStatus.AVAILABLE,
        max_length=1,
    )

    class BookCover(models.TextChoices):
        HARDBACK = ("H", "Hardback")
        PAPERBAK = ("P", "Paperback")
        EBOOK = ("E", "E-book")

    cover_type = models.TextField(
        "Cover Type",
        choices=BookCover.choices,
        max_length=1,
    )

    isbn = models.CharField(
        "ISBN",
        max_length=13,
        unique=False,
        help_text="""Defaults to Book ISBN if not value entered""",  # noqa
        blank=True,
        null=True,
    )

    publish_date = models.DateField(
        "Published On",
        blank=True,
        null=True,
    )

    item_language = models.ManyToManyField(
        Language,
        related_name="book_copy_language",
    )

    def __str__(self):
        return f"{self.book.title}"

    def save(self, *args, **kwargs):
        if not self.isbn:
            self.isbn = self.book.isbn
        if not self.publish_date:
            self.publish_date = self.book.publish_date
        super().save(*args, **kwargs)
