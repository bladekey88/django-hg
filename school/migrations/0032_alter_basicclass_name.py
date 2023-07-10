# Generated by Django 4.2.1 on 2023-07-10 22:08

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("school", "0031_basicclass_slug"),
    ]

    operations = [
        migrations.AlterField(
            model_name="basicclass",
            name="name",
            field=models.CharField(
                max_length=100,
                unique=True,
                validators=[django.core.validators.MinLengthValidator(5)],
                verbose_name="Class Name",
            ),
        ),
    ]
