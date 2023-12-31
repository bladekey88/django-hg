# Generated by Django 4.2.1 on 2023-08-17 16:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0011_alter_borrowerfine_resolved_date"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="borrowerfine",
            options={
                "verbose_name": "Borrower Fine",
                "verbose_name_plural": "Borrower Fines",
            },
        ),
        migrations.AlterField(
            model_name="bookinstance",
            name="due_back",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="borrower",
            name="borrow_limit",
            field=models.PositiveIntegerField(
                blank=True, default=0, null=True, verbose_name="Maximum Number of Items"
            ),
        ),
    ]
