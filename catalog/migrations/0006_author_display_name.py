# Generated by Django 4.2.1 on 2023-08-16 13:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0005_borrower_fine_borrowerfine_borrower_fines_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="author",
            name="display_name",
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
