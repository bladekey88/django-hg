# Generated by Django 4.2.1 on 2023-07-07 19:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("school", "0027_basiccourse_slug"),
    ]

    operations = [
        migrations.AlterField(
            model_name="basiccourse",
            name="slug",
            field=models.SlugField(unique=True),
        ),
    ]
