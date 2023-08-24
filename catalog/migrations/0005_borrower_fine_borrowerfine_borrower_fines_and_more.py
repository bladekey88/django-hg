# Generated by Django 4.2.1 on 2023-08-13 19:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("catalog", "0004_alter_bookinstance_status"),
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
                        blank=True, default=0.0, null=True, verbose_name="Fine Amount"
                    ),
                ),
                (
                    "borrow_limit",
                    models.PositiveIntegerField(
                        blank=True,
                        default=0,
                        null=True,
                        verbose_name="Maximum Items able to be Checked Out",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Fine",
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
                    models.CharField(
                        max_length=50, unique=True, verbose_name="Fine Name"
                    ),
                ),
                ("value", models.FloatField(verbose_name="Fine Amount")),
                (
                    "fine_frequency",
                    models.CharField(
                        choices=[
                            ("H", "Hourly"),
                            ("D", "Daily"),
                            ("W", "Weekly"),
                            ("M", "Monthly"),
                            ("O", "One-Offf"),
                        ],
                        default="D",
                        max_length=1,
                        verbose_name="Fine Charge Frequency",
                    ),
                ),
            ],
            options={
                "verbose_name": "Fine",
                "verbose_name_plural": "Fines",
            },
        ),
        migrations.CreateModel(
            name="BorrowerFine",
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
                    "borrower",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="catalog.borrower",
                    ),
                ),
                (
                    "fine",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="catalog.fine"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="borrower",
            name="fines",
            field=models.ManyToManyField(
                blank=True,
                through="catalog.BorrowerFine",
                to="catalog.fine",
                verbose_name="Fines",
            ),
        ),
        migrations.AddField(
            model_name="borrower",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
    ]