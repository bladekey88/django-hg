# Generated by Django 4.2.1 on 2023-05-21 14:48

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0019_rename_user_quidditchplayer_student"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="quidditchplayer",
            name="is_player",
        ),
    ]