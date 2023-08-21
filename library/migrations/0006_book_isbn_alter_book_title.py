# Generated by Django 4.2.1 on 2023-08-19 19:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("library", "0005_alter_book_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="book",
            name="isbn",
            field=models.CharField(
                default=1,
                help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>',
                max_length=13,
                unique=True,
                verbose_name="ISBN",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="book",
            name="title",
            field=models.CharField(
                help_text="Enter the name/title for this item",
                max_length=200,
                verbose_name="title",
            ),
        ),
    ]
