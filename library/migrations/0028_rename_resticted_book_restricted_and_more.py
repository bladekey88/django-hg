# Generated by Django 4.2.1 on 2023-08-29 19:49

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("library", "0027_book_resticted_book_visible_videogame_resticted_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="book",
            old_name="resticted",
            new_name="restricted",
        ),
        migrations.RenameField(
            model_name="videogame",
            old_name="resticted",
            new_name="restricted",
        ),
    ]
