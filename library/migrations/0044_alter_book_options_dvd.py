# Generated by Django 4.2.5 on 2023-09-10 15:57

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("library", "0043_alter_book_options"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="book",
            options={
                "ordering": ["series", "position_in_series", "title"],
                "verbose_name": "Book",
                "verbose_name_plural": "Books",
            },
        ),
        migrations.CreateModel(
            name="DVD",
            fields=[
                (
                    "title",
                    models.CharField(
                        help_text="Enter the name/title for this item",
                        max_length=200,
                        verbose_name="title",
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
                        editable=False,
                        help_text="Unique ID for this particular item across whole library",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "publish_date",
                    models.DateField(
                        blank=True, null=True, verbose_name="First Published On"
                    ),
                ),
                (
                    "part_of_series",
                    models.BooleanField(
                        blank=True,
                        default=False,
                        null=True,
                        verbose_name="Part of Series",
                    ),
                ),
                (
                    "position_in_series",
                    models.IntegerField(
                        blank=True, null=True, verbose_name="Number in Series"
                    ),
                ),
                (
                    "item_type",
                    models.CharField(
                        choices=[
                            ("B", "Book"),
                            ("D", "Digital"),
                            ("CD", "Compact Disc"),
                            ("V", "Video Game"),
                        ],
                        editable=False,
                        max_length=7,
                        verbose_name="Item Type",
                    ),
                ),
                (
                    "visible",
                    models.BooleanField(default=True, verbose_name="Item Visible"),
                ),
                (
                    "restricted",
                    models.BooleanField(default=False, verbose_name="Item Restricted"),
                ),
                ("author", models.ManyToManyField(to="library.author")),
                (
                    "genre",
                    models.ManyToManyField(
                        help_text="Select a genre for this item", to="library.genre"
                    ),
                ),
                (
                    "item_language",
                    models.ManyToManyField(
                        related_name="Language", to="library.language"
                    ),
                ),
                (
                    "series",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="library.series",
                    ),
                ),
            ],
            options={
                "verbose_name": "DVD",
                "verbose_name_plural": "DVDs",
                "default_permissions": ("add", "change", "delete", "view"),
            },
        ),
    ]
