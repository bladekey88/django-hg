# Generated by Django 4.2.1 on 2023-06-05 13:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0035_alter_parent_children_alter_parent_related_parent"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="is_staff",
            field=models.BooleanField(
                default=False, verbose_name="Access Managed Area"
            ),
        ),
    ]