# Generated by Django 4.2.1 on 2023-05-21 15:37

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0020_remove_quidditchplayer_is_player"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="quidditchplayer",
            options={
                "ordering": ["student"],
                "verbose_name": "Quidditch Player",
                "verbose_name_plural": "Quidditch Players",
            },
        ),
    ]
