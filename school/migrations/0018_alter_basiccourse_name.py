# Generated by Django 4.2.1 on 2023-06-06 13:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("school", "0017_alter_basicclass_class_code"),
    ]

    operations = [
        migrations.AlterField(
            model_name="basiccourse",
            name="name",
            field=models.CharField(
                max_length=50, unique=True, verbose_name="Course Name"
            ),
        ),
    ]