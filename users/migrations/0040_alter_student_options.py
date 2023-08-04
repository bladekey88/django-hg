# Generated by Django 4.2.1 on 2023-07-30 21:29

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0039_alter_student_test_house"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="student",
            options={
                "ordering": ("user__last_name",),
                "permissions": [("enrol_student", "Can sign up student to a course")],
                "verbose_name": "Student",
                "verbose_name_plural": "Students",
            },
        ),
    ]