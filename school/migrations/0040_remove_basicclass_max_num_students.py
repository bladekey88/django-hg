# Generated by Django 4.2.1 on 2023-07-30 22:28

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("school", "0039_basicclass_max_num_students"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="basicclass",
            name="max_num_students",
        ),
    ]
