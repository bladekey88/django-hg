# Generated by Django 4.2.1 on 2023-08-29 14:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("library", "0023_alter_videogame_item_type"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="borrower",
            options={
                "ordering": ["user__last_name", "user__first_name"],
                "verbose_name": "Borrower",
                "verbose_name_plural": "Borrowers",
            },
        ),
        migrations.AlterField(
            model_name="borrower",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="library_user",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Member",
            ),
        ),
        migrations.AlterField(
            model_name="videogame",
            name="item_type",
            field=models.CharField(
                default="V", editable=False, max_length=15, verbose_name="Type"
            ),
        ),
    ]