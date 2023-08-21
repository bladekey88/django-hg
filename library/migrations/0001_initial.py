# Generated by Django 4.2.1 on 2023-08-19 19:12

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Author",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(max_length=100, verbose_name="First Name"),
                ),
                (
                    "middle_name",
                    models.CharField(
                        blank=True,
                        max_length=100,
                        null=True,
                        verbose_name="Middle Name",
                    ),
                ),
                (
                    "last_name",
                    models.CharField(max_length=100, verbose_name="Last Name"),
                ),
                (
                    "display_name",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "date_of_birth",
                    models.DateField(blank=True, null=True, verbose_name="Born"),
                ),
                (
                    "date_of_death",
                    models.DateField(blank=True, null=True, verbose_name="Died"),
                ),
                (
                    "author_type",
                    models.CharField(
                        blank=True,
                        choices=[("I", "Individual"), ("G", "Group"), ("C", "Company")],
                        default="I",
                        max_length=10,
                        verbose_name="Author Type",
                    ),
                ),
            ],
            options={
                "ordering": ["last_name", "first_name"],
            },
        ),
        migrations.CreateModel(
            name="Genre",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "Name",
                    models.CharField(
                        help_text="Enter a book genre (e.g. Science Fiction)",
                        max_length=200,
                        unique=True,
                    ),
                ),
                (
                    "Type",
                    models.CharField(
                        choices=[("F", "Fiction"), ("NF", "Non-Fiction")],
                        help_text="Choose Genre Type",
                        max_length=10,
                        verbose_name="Type",
                    ),
                ),
            ],
            options={
                "ordering": ["Name"],
            },
        ),
        migrations.CreateModel(
            name="Series",
            fields=[
                (
                    "name",
                    models.CharField(
                        max_length=200, unique=True, verbose_name="Series Name"
                    ),
                ),
                (
                    "summary",
                    models.TextField(
                        help_text="Enter a brief description of the item",
                        max_length=1000,
                    ),
                ),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        help_text="Unique ID for this particular item across whole library",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "publish_date",
                    models.DateField(
                        blank=True, null=True, verbose_name="Published On"
                    ),
                ),
                ("author", models.ManyToManyField(to="library.author")),
                (
                    "genre",
                    models.ManyToManyField(
                        help_text="Select a genre for this item", to="library.genre"
                    ),
                ),
            ],
        ),
    ]
