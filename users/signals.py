from django.dispatch import receiver
import django_auth_ldap.backend
from users.models import Student, CustomUser, QuidditchPlayer, Staff, Parent
from django.db.models.signals import post_save, post_delete
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from userprofile.config import ConfigGroup

# TO DO - create separate function for account type creation#
#  (e.g create_student, create_staff etc) so we can adhere to DRY


def populate_user_profile(sender, user, ldap_user, **kwargs):
    """
    Signal Handler that determines what Profile Type is needed and populates
    the attributes appropriately. This will get called after authentication
    against LDAP and core CustomUser/user attributes are mapped,
    """
    data = {}
    account_type = str(ldap_user.attrs["employeeType"][0]).lower()
    user.created_externally = True
    user.save()

    all_users_group = Group.objects.get(name=ConfigGroup.ALL_USERS)
    if not user.groups.filter(name=all_users_group.name).exists():
        user.groups.add(all_users_group)

    # Suspension Check
    if not user.is_superuser:
        ldap_suspension_state = ldap_user.attrs.get("suspendedAccount")[0]
        if ldap_suspension_state == str(user.is_active).upper():
            if ldap_suspension_state == "TRUE":
                user.is_active = False
            elif ldap_suspension_state == "FALSE":
                user.is_active = True
            user.save()

    if not user.is_active:
        return False

    if CustomUser.objects.filter(uid=user.uid).exists():
        """
        Check to see the user is a student or not. If they aren't create
        them as a Student object.
        """
        if account_type == "student":
            try:
                user.student
            except Student.DoesNotExist:
                Student.objects.create(user=user)

            """
            Initial  Student attributes are School House, School Year, and
            Prefect status. If a value from LDAP is supplied then we use that,
            otherwise we fall back to the model default value for the
            attribute. We also create a linked Quidditch object as needed.
            LDAP does not currently store the granular quidditch attributes
            at this time so those values  fall-back to model default.
            """
            house_raw = ldap_user.attrs.get("schoolHouse")
            year_raw = ldap_user.attrs.get("schoolYear")
            prefect_raw = ldap_user.attrs.get("prefect")

            # HOUSE
            """
            Create a dictionary of house names and values from enum
            ldap returns are list, so grab first element and
            look it up in dictionary using get (and upper due to enum)
            """
            houses = {house.name: house.value for house in Student.House}
            if house_raw:
                data["house"] = houses.get(house_raw[0].upper(), Student.House.UNSORTED)

            # YEAR
            if year_raw:
                years = {year.name: year.value for year in Student.Year}
                data["year"] = years.get(
                    year_raw[0].split(" ")[0].upper(), Student.Year.UNKNOWN
                )

            # PREFECT
            data["prefect"] = (
                True if prefect_raw and prefect_raw[0] == "TRUE" else False
            )

            # Set all attributes and save the object
            for key, value in data.items():
                if value is not None:
                    setattr(user.student, key, value)
            user.student.save()

            # Quidditch object needs to be created and linked via Student FK
            quidditch_raw = ldap_user.attrs.get("quidditchPlayer")
            if quidditch_raw and quidditch_raw[0] == "TRUE":
                try:
                    user.student.quidditchplayer
                except QuidditchPlayer.DoesNotExist:
                    try:
                        QuidditchPlayer.objects.create(student=user.student)
                    except ValidationError as e:
                        raise ValueError(f"Invalid Data in underlying Student: {e}")

        elif account_type == "staff":
            try:
                user.staff
            except Exception:
                Staff.objects.create(user=user)

            # HEAD OF HOUSE
            head_of_house_raw = ldap_user.attrs.get("headofHouse")
            if head_of_house_raw and head_of_house_raw[0] == "TRUE":
                data["is_head_of_house"] = True
                user.groups.add(
                    Group.objects.get(name=ConfigGroup.HEADS_OF_HOUSE_GROUP)
                )
            else:
                data["is_head_of_house"] = False
                user.groups.remove(
                    Group.objects.get(name=ConfigGroup.HEADS_OF_HOUSE_GROUP)
                )

            for key, value in data.items():
                if value:
                    setattr(user.staff, key, value)
            user.staff.save()


#######################
# Signal for user population
# Passes the function above which gets called first before create_user_profile
# function if via LDAP, other create_user_profile runs
#######################
django_auth_ldap.backend.populate_user.connect(populate_user_profile)


#######################
# USER FIRST TIME LOGIN
#######################
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """
    On creation (via any method), activate receiver and assign to groups
    The (Custom)User object has been created and now post-processing.
    For most function, a derivative object is used rather than the base
    CustomUser Object (People Types, Student/Staff/Parent) have a relationship
    to the CU object.
    """
    if created:
        # Add to All Users Group
        all_users_group = Group.objects.get(name="All Users")
        instance.groups.add(all_users_group)

        # Create the profile object based on the user's account type
        # Check that LDAP is creating the user, else skip processing
        if hasattr(instance, "ldap_user"):
            account_type = instance.ldap_user.attrs.get("employeeType")[0].lower()
            if account_type == "student":
                profile = Student.objects.create(user=instance)
            elif account_type == "staff":
                profile = Staff.objects.create(user=instance)
            elif account_type == "parent":
                profile = Parent.objects.create(user=instance)
            else:
                raise ValueError("Invalid Account Type")

            """
            Initial  Student attributes are School House, School Year, and
            Prefect status. If a value from LDAP is supplied then we use that,
            otherwise we fall back to the model default value for the
            attribute. We also create a linked Quidditch object as needed.
            LDAP does not currently store the granular quidditch attributes
            at this time so those values  fall-back to model default.
            """
            if account_type == "student":
                house_raw = instance.ldap_user.attrs.get("schoolHouse")
                houses = Student.House.labels
                if house_raw and house_raw[0] in houses:
                    profile.house = house_raw[0][0:2].upper()

                year_raw = instance.ldap_user.attrs.get("schoolYear")
                years = Student.Year
                profile.year = years.labels.index(year_raw[0].split(" ")[0])

                prefect_raw = instance.ldap_user.attrs.get("prefect")
                if prefect_raw and prefect_raw[0] == "TRUE":
                    profile.prefect = True

            if account_type == "staff":
                if hasattr(profile, "is_head_of_house"):
                    profile.is_head_of_house = (
                        instance.ldap_user.attrs.get("headofHouse")[0] == "TRUE"
                    )
            # Save the profile object.
            profile.save()

            # Add Quidditch
            if account_type == "student":
                quidditch_raw = instance.ldap_user.attrs.get("quidditchPlayer")
                if quidditch_raw[0] == "TRUE":
                    QuidditchPlayer.objects.create(student=profile)

            # Handle Remaining Group Memberships
            # if account_type == "student":
            #     all_students_group = Group.objects.get(name="All Students")
            #     instance.groups.add(all_students_group)
            if account_type == "staff":
                all_staff_group = Group.objects.get(name=ConfigGroup.ALL_STAFF)
                instance.groups.add(all_staff_group)
            elif account_type == "parent":
                all_parents_group = Group.objects.get(name=ConfigGroup.ALL_PARENT)
                instance.groups.add(all_parents_group)


@receiver(post_save, sender=Student)
def handle_add_student_group(sender, instance, created, **kwargs):
    all_students_group = Group.objects.get(name=ConfigGroup.ALL_STUDENT)
    if not instance.user.groups.filter(name=all_students_group.name).exists():
        instance.user.groups.add(all_students_group)


@receiver(post_delete, sender=Student)
def handle_remove_student_group(sender, instance, **kwargs):
    all_students_group = Group.objects.get(name=ConfigGroup.ALL_STUDENT)
    instance.user.groups.remove(all_students_group)


@receiver(post_save, sender=Staff)
def handle_add_staff_group(sender, instance, created, **kwargs):
    all_staff_group = Group.objects.get(name=ConfigGroup.ALL_STAFF)
    if not instance.user.groups.filter(name=all_staff_group.name).exists():
        instance.user.groups.add(all_staff_group)


@receiver(post_delete, sender=Staff)
def handle_remove_staff_group(sender, instance, **kwargs):
    all_staff_group = Group.objects.get(name=ConfigGroup.ALL_STAFF)
    hoh_group = Group.objects.get(name=ConfigGroup.HEADS_OF_HOUSE)
    instance.user.groups.remove(all_staff_group)
    instance.user.groups.remove(hoh_group)
