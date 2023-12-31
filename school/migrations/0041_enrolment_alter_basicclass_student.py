# Generated by Django 4.2.1 on 2023-08-02 21:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0040_alter_student_options"),
        ("school", "0040_remove_basicclass_max_num_students"),
    ]

    operations = [
        migrations.CreateModel(
            name="Enrolment",
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
                ("created_date", models.DateTimeField(auto_now_add=True)),
                ("modified_date", models.DateTimeField(auto_now=True)),
                (
                    "student_class_status",
                    models.CharField(
                        choices=[
                            ("A", "Active"),
                            ("E", "Expired"),
                            ("N", "Not Eligible"),
                            ("P", "Pending"),
                            ("S", "Suspended"),
                        ],
                        max_length=1,
                        verbose_name="Status",
                    ),
                ),
                (
                    "basic_class",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="school.basicclass",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="users.student"
                    ),
                ),
            ],
            options={
                "verbose_name": "Enrolment",
                "verbose_name_plural": "Enrolments",
            },
        ),
        migrations.RemoveField(
            model_name="basicclass",
            name = "student",
            ),
        migrations.AddField(
            model_name="basicclass",
            name="student",
            field=models.ManyToManyField(
                blank=True,
                through="school.Enrolment",
                to="users.student",
                verbose_name="student",
            ),
        ),
    ]
