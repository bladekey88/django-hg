# Generated by Django 4.2.1 on 2023-08-20 17:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("library", "0010_genre_object"),
    ]

    operations = [
        migrations.AlterField(
            model_name="genre",
            name="Type",
            field=models.CharField(
                blank=True,
                choices=[("F", "Fiction"), ("NF", "Non-Fiction")],
                help_text="Choose Genre Type",
                max_length=10,
                null=True,
                verbose_name="Type",
            ),
        ),
    ]