# Generated by Django 4.2.1 on 2023-08-19 19:20

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("library", "0002_alter_genre_options_remove_genre_name_genre_name"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="series",
            options={
                "ordering": ["name"],
                "verbose_name": "Series",
                "verbose_name_plural": "Series",
            },
        ),
    ]
