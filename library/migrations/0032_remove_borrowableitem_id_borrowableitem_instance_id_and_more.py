# Generated by Django 4.2.1 on 2023-09-04 15:23

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("library", "0031_remove_borrowableitem_book_item_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="borrowableitem",
            name="id",
        ),
        migrations.AddField(
            model_name="borrowableitem",
            name="instance_id",
            field=models.UUIDField(
                default=uuid.uuid4, primary_key=True, serialize=False
            ),
        ),
        migrations.AlterField(
            model_name="borrowableitem",
            name="object_id",
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]