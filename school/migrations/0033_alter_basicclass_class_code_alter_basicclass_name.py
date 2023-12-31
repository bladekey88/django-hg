# Generated by Django 4.2.1 on 2023-07-10 23:01

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("school", "0032_alter_basicclass_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="basicclass",
            name="class_code",
            field=models.CharField(
                blank=True,
                editable=False,
                max_length=20,
                null=True,
                unique=True,
                verbose_name="Class Code",
            ),
        ),
        migrations.AlterField(
            model_name="basicclass",
            name="name",
            field=models.CharField(
                max_length=100,
                unique=True,
                validators=[django.core.validators.MinLengthValidator(3)],
                verbose_name="Class Name",
            ),
        ),
    ]
