# Generated by Django 4.2.1 on 2023-08-22 13:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("library", "0018_alter_book_options_alter_videogame_options_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Language",
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
                    "name",
                    models.CharField(max_length=256, verbose_name="Language name"),
                ),
                (
                    "name_local",
                    models.CharField(
                        blank=True,
                        default="",
                        max_length=256,
                        verbose_name="Language name (in that language)",
                    ),
                ),
                (
                    "isocode",
                    models.CharField(
                        help_text="2 character language code without country",
                        max_length=2,
                        unique=True,
                        verbose_name="ISO 639-1 Language code",
                    ),
                ),
                (
                    "sorting",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="Increase to show at top of the list",
                        verbose_name="Sort Order",
                    ),
                ),
            ],
            options={
                "verbose_name": "language",
                "verbose_name_plural": "languages",
                "ordering": ("-sorting", "name", "isocode"),
            },
        ),
    ]