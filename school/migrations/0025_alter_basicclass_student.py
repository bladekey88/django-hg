# Generated by Django 4.2.1 on 2023-06-15 17:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0036_alter_customuser_is_staff"),
        ("school", "0024_alter_schoolyear_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="basicclass",
            name="student",
            field=models.ManyToManyField(
                blank=True, null=True, to="users.student", verbose_name="student"
            ),
        ),
    ]
