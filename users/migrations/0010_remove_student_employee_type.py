# Generated by Django 4.2.1 on 2023-05-17 12:05

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0009_student_employee_type"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="student",
            name="employee_type",
        ),
    ]
