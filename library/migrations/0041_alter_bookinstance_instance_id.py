# Generated by Django 4.2.1 on 2023-09-04 16:37

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("library", "0040_bookinstance_delete_borrowablebook"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bookinstance",
            name="instance_id",
            field=models.UUIDField(
                default=uuid.uuid4,
                editable=False,
                help_text="Unique ID for this particular book instance across whole library",
                primary_key=True,
                serialize=False,
            ),
        ),
    ]