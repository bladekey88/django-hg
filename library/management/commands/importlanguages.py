from django.core.management.base import BaseCommand, CommandError
from library.models import Language
from django.conf.locale import LANG_INFO


class Command(BaseCommand):
    help = "Imports language codes and names from django.conf.locale.LANG_INFO"
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument(
            "--overwrite",
            help="Force sync to overwrite values instead of skipping",
            action="store_true",
        )

    def handle(self, *args, **options):
        cnt = 0
        for lang in LANG_INFO:
            if len(lang) == 2:  # Only care about the 2 letter iso codes
                try:
                    core_lang = Language.objects.get(isocode=lang)
                    if options["overwrite"]:
                        core_lang.isocode = lang
                        core_lang.name = LANG_INFO[lang]["name"]
                        core_lang.name_local = LANG_INFO[lang]["name_local"]
                        core_lang.save()
                        cnt += 1
                        self.stdout.write(f"Overwrote {lang}")
                except Language.DoesNotExist:  # Doesn't exist, so create it!
                    core_lang = Language(
                        isocode=lang,
                        name=LANG_INFO[lang]["name"],
                        name_local=LANG_INFO[lang]["name_local"],
                    )
                    core_lang.save()
                    cnt = +1

        self.stdout.write(f"Added {cnt} languages to library")
