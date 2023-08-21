# Generated by Django 4.2.1 on 2023-08-21 16:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("library", "0016_alter_author_options_alter_genre_options"),
    ]

    operations = [
        migrations.CreateModel(
            name="Borrower",
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
                    "status",
                    models.CharField(
                        choices=[
                            ("A", "Active"),
                            ("S", "Suspended"),
                            ("P", "Pending"),
                            ("('I', 'Inactive')", "Inactive"),
                        ],
                        default="P",
                        max_length=17,
                        verbose_name="Borrower Status",
                    ),
                ),
                (
                    "max_fine_amount",
                    models.FloatField(
                        blank=True,
                        default=0.0,
                        help_text="This is the maximum fine a user can accrue before borrowing privileges are revoked",
                        null=True,
                        verbose_name="Maximum Fine Amount",
                    ),
                ),
                (
                    "borrow_limit",
                    models.PositiveIntegerField(
                        blank=True,
                        default=0,
                        help_text="The maximum number of items a user can borrow at any one time",
                        null=True,
                        verbose_name="Maximum Number of Items",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="library_user",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Borrower",
                "verbose_name_plural": "Borrowers",
            },
        ),
    ]
