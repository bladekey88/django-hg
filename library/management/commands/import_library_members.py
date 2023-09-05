from django.core.management.base import BaseCommand, CommandError
from library.models import Borrower
from users.models import CustomUser
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = "Imports all users from CustomUser Model into Library and set them as active"
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument(
            "--overwrite",
            "-O",
            help="Force sync to overwrite values instead of skipping",
            action="store_true",
        )

    def handle(self, *args, **options):
        for cnt, cuser in enumerate(CustomUser.objects.all()):
            try:
                # reverse rel for borrower is library_user as defined in model
                borrower = cuser.library_user
                if options["overwrite"]:
                    borrower.user = cuser
                    if not cuser.is_active:
                        borrower.status = Borrower.BorrowerStatus.INACTIVE
                    elif (
                        cuser.is_active
                        and borrower.status == Borrower.BorrowerStatus.INACTIVE
                    ):
                        borrower.status = Borrower.BorrowerStatus.PENDING
                    borrower.save()
                    self.stdout.write(f"Overwrote {cuser.full_common_name()}")

            except Borrower.DoesNotExist:  # Doesn't exist, so create it!
                new_borrower = Borrower(
                    user=cuser, status=Borrower.BorrowerStatus.PENDING
                )
                new_borrower.save()
                cuser.groups.add(Group.objects.get(name="Library Members"))

                self.stdout.write(
                    f"Added {new_borrower.user.full_common_name()} to library (Pending Status)"
                )
