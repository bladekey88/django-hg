# Generated by Django 4.2.1 on 2023-08-04 14:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("school", "0046_rename_course_category_basiccourse_category"),
    ]

    operations = [
        migrations.AlterField(
            model_name="basiccourse",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="school.coursecategory"
            ),
        ),
    ]
