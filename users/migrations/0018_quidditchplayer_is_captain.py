# Generated by Django 4.2.1 on 2023-05-21 14:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0017_alter_quidditchplayer_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="quidditchplayer",
            name="is_captain",
            field=models.BooleanField(default=False, verbose_name="Is Captain"),
        ),
    ]
