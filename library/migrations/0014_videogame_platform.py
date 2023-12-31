# Generated by Django 4.2.1 on 2023-08-20 20:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("library", "0013_alter_videogame_genre"),
    ]

    operations = [
        migrations.AddField(
            model_name="videogame",
            name="platform",
            field=models.CharField(
                choices=[
                    ("NES", "Nintendo Enetertainment System"),
                    ("SNES", "Super Nintendo Entertainment System"),
                    ("N64", "Nintendo 64"),
                    ("GC", "Nintendo Gamecube"),
                    ("WII", "Nintendo Wii"),
                    ("WIIU", "Wii-U"),
                    ("SWITCH", "Nintendo Switch"),
                    ("GB", "Gameboy"),
                    ("GBC", "Gameboy Color"),
                    ("GBA", "Gameboy Advance"),
                    ("DS", "Nintendo DS"),
                    ("3DS", "3DS"),
                    ("PS1", "Playstation 1"),
                    ("PS2", "Playstation 2"),
                    ("PS3", "Playstation 3"),
                    ("PS4", "Playstation 4"),
                    ("PS5", "Playstation 5"),
                    ("XBOX", "XBox"),
                    ("X360", "XBox 360"),
                    ("XONE", "XBox One"),
                    ("XSXSE", "XBox Series X/S"),
                ],
                default="PS2",
                max_length=10,
                verbose_name="Platform",
            ),
            preserve_default=False,
        ),
    ]
