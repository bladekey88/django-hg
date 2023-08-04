# Generated by Django 4.2.1 on 2023-08-04 13:05

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("school", "0042_enrolment_unique_student_class"),
    ]

    operations = [
        migrations.CreateModel(
            name="CourseCategory",
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
                        max_length=50,
                        unique=True,
                        validators=[
                            django.core.validators.MinLengthValidator(3),
                            django.core.validators.RegexValidator("^[a-zA-Z0-9]*$"),
                        ],
                        verbose_name="Category Name",
                    ),
                ),
                (
                    "code",
                    models.CharField(
                        max_length=6,
                        unique=True,
                        validators=[django.core.validators.MinLengthValidator(3)],
                        verbose_name="Category Code",
                    ),
                ),
            ],
            options={
                "verbose_name": "Course Category",
                "verbose_name_plural": "Course Categories",
                "ordering": ["name"],
            },
        ),
        migrations.AlterModelOptions(
            name="enrolment",
            options={
                "ordering": ["student__user__last_name"],
                "verbose_name": "Enrolment",
                "verbose_name_plural": "Enrolments",
            },
        ),
    ]