# Generated by Django 4.2.1 on 2023-06-05 15:02

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("school", "0006_alter_schoolyear_start_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="schoolyear",
            name="start_date",
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
