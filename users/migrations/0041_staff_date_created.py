# Generated by Django 4.2.5 on 2023-09-10 18:30

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0040_alter_student_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="staff",
            name="date_created",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
    ]
