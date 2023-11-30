# Generated by Django 4.2.5 on 2023-11-30 14:03

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0044_alter_customuser_date_joined_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="student",
            options={
                "ordering": ("user__last_name",),
                "verbose_name": "Student",
                "verbose_name_plural": "Students",
            },
        ),
        migrations.AlterField(
            model_name="customuser",
            name="date_joined",
            field=models.DateTimeField(
                default=django.utils.timezone.now,
                editable=False,
                verbose_name="Date Joined",
            ),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="last_login",
            field=models.DateTimeField(
                blank=True,
                default=None,
                editable=False,
                null=True,
                verbose_name="Last Logged In",
            ),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="uid",
            field=models.CharField(max_length=30, unique=True, verbose_name="Username"),
        ),
        migrations.AlterField(
            model_name="staff",
            name="date_created",
            field=models.DateTimeField(auto_now_add=True, verbose_name="Date Created"),
        ),
        migrations.AlterField(
            model_name="staff",
            name="is_head_of_house",
            field=models.BooleanField(default=False, verbose_name="Is Head Of House"),
        ),
    ]