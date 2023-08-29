# Generated by Django 4.2.1 on 2023-08-29 16:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("library", "0024_alter_borrower_options_alter_borrower_user_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="borrower",
            name="borrow_limit",
            field=models.PositiveIntegerField(
                blank=True,
                default=5,
                help_text="Maximum number of items a user can borrow at any one time",
                null=True,
                verbose_name="Maximum Number of Items",
            ),
        ),
        migrations.AlterField(
            model_name="borrower",
            name="max_fine_amount",
            field=models.FloatField(
                blank=True,
                default=5.0,
                help_text="Maximum fine before revoking borrowing privileges",
                null=True,
                verbose_name="Maximum Fine Amount",
            ),
        ),
    ]
