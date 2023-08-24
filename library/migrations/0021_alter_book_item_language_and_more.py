# Generated by Django 4.2.1 on 2023-08-22 14:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("library", "0020_remove_book_item_language_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="book",
            name="item_language",
            field=models.ManyToManyField(
                default="English", related_name="book_language", to="library.language"
            ),
        ),
        migrations.AlterField(
            model_name="videogame",
            name="item_language",
            field=models.ManyToManyField(
                default="English",
                related_name="videogame_language",
                to="library.language",
            ),
        ),
    ]