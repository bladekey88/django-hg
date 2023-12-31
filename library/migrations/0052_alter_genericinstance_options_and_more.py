# Generated by Django 4.2.5 on 2023-09-18 19:27

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("library", "0051_alter_genericinstance_object_id"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="genericinstance",
            options={},
        ),
        migrations.AlterField(
            model_name="genericinstance",
            name="content_type",
            field=models.ForeignKey(
                limit_choices_to=models.Q(
                    models.Q(("app_label", "library"), ("model", "Book")),
                    models.Q(("app_label", "library"), ("model", "VideoGame")),
                    _connector="OR",
                ),
                on_delete=django.db.models.deletion.CASCADE,
                to="contenttypes.contenttype",
            ),
        ),
        migrations.AlterField(
            model_name="genericinstance",
            name="object_id",
            field=models.UUIDField(verbose_name="Object ID"),
        ),
        migrations.CreateModel(
            name="CheckOut",
            fields=[
                (
                    "instance_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="Unique ID for this particular videogame instance across whole library",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("checkout_date", models.DateTimeField(auto_now_add=True)),
                ("modified_date", models.DateTimeField(auto_now=True)),
                ("due_date", models.DateTimeField()),
                ("return_date", models.DateTimeField(blank=True, null=True)),
                (
                    "borrower",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="borrower",
                        to="library.borrower",
                    ),
                ),
                (
                    "issuer",
                    models.ForeignKey(
                        limit_choices_to={"is_librarian": True},
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="issuer",
                        to="library.borrower",
                    ),
                ),
                (
                    "item_instance",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="library.genericinstance",
                    ),
                ),
            ],
        ),
    ]
