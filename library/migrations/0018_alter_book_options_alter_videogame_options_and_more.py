# Generated by Django 4.2.1 on 2023-08-21 21:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("library", "0017_borrower"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="book",
            options={
                "ordering": ["series", "position_in_series", "title"],
                "verbose_name": "Book",
                "verbose_name_plural": "Books",
            },
        ),
        migrations.AlterModelOptions(
            name="videogame",
            options={
                "ordering": ["series", "position_in_series", "title"],
                "verbose_name": "Video Game",
                "verbose_name_plural": "Video Games",
            },
        ),
        migrations.AlterField(
            model_name="author",
            name="first_name",
            field=models.CharField(
                blank=True, max_length=100, null=True, verbose_name="First Name"
            ),
        ),
    ]