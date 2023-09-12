# Generated by Django 4.2.1 on 2023-09-04 18:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("library", "0041_alter_bookinstance_instance_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="series",
            name="series_size",
            field=models.PositiveIntegerField(
                blank=True, null=True, verbose_name="Number of Items in Series"
            ),
        ),
    ]