# Generated by Django 4.2.1 on 2023-05-16 20:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0006_customuser_uid"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="uid",
            field=models.CharField(max_length=20, unique=True, verbose_name="User ID"),
        ),
    ]
