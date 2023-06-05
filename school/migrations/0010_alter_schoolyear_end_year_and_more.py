# Generated by Django 4.2.1 on 2023-06-05 15:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("school", "0009_alter_schoolyear_options_alter_schoolyear_end_year_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="schoolyear",
            name="end_year",
            field=models.BigIntegerField(editable=False, verbose_name="End Year"),
        ),
        migrations.AlterField(
            model_name="schoolyear",
            name="start_date",
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name="schoolyear",
            name="start_year",
            field=models.BigIntegerField(editable=False, verbose_name="Start Year"),
        ),
        migrations.AddConstraint(
            model_name="schoolyear",
            constraint=models.UniqueConstraint(
                fields=("start_year", "end_year"), name="unique_year_period"
            ),
        ),
    ]
