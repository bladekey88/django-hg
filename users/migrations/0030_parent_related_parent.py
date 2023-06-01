# Generated by Django 4.2.1 on 2023-06-01 16:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0029_remove_parent_linked_to_other_parent"),
    ]

    operations = [
        migrations.AddField(
            model_name="parent",
            name="related_parent",
            field=models.ManyToManyField(
                blank=True, default=None, max_length=5, null=True, to="users.parent"
            ),
        ),
    ]
