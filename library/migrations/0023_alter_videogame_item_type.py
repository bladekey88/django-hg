# Generated by Django 4.2.1 on 2023-08-24 16:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("library", "0022_alter_series_options_rename_name_series_title_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="videogame",
            name="item_type",
            field=models.CharField(default="V", max_length=15, verbose_name="Type"),
        ),
    ]
