from .models import Borrower
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.contrib.auth.models import Group

# GROUPS TO ADD USERS TO
STANDARD_LIBRARY_GROUP = Group.objects.get(name="Library Members")
PRIVILEGED_LIBRARY_GROUP = Group.objects.get(name="Librarians")
library_groups = [STANDARD_LIBRARY_GROUP, PRIVILEGED_LIBRARY_GROUP]


# Save after updating or creating borrower record
@receiver(post_save, sender=Borrower)
def add_library_group_membership(sender, created, instance, **kwargs):
    # Groups are assigned at user level (CU model) so need to traverse back
    # from Borrower to CustomUser
    user = instance.user

    # Object is being created so we can assign straight to group
    if created:
        user.groups.add(STANDARD_LIBRARY_GROUP)


# Remove from groups after Borrower Record is deleted
@receiver(post_delete, sender=Borrower)
def remove_library_group_membership(sender, instance, **kwargs):
    user = instance.user
    for library_group in library_groups:
        user.groups.remove(library_group)
