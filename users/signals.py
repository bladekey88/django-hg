from django.dispatch import receiver
import django_auth_ldap.backend
from users.models import Student, CustomUser, QuidditchPlayer, Staff
from django.db.models.signals import post_save
from django.contrib.auth.models import Group

# TO DO - create separate function for account type creation#
#  (e.g create_student, create_staff etc) so we can adhere to DRY


def populate_user_profile(sender, user, ldap_user, **kwargs):
    """
    Signal Handler that determines what Profile Type is needed and populates
    the attributes appropriately. This will get called after authentication
    against LDAP and core CustomUser/user attributes are mapped,
    """
    temp_profile = None
    data = {}
    account_type = str(ldap_user.attrs["employeeType"][0]).lower()

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
                temp_profile = user.student
            except Exception:
                temp_profile = Student.objects.create(user=user)

            """
            Initial  Student attributes are School House, School Year, and 
            Prefect status. If a value from LDAP is supplied then we use that,
            otherwise we fall back to the model default value for the
            attribute. We also create a linked Quidditch object as needed.
            LDAP does not currently store the granular quidditch attributes
            at this time so those values  fall-back to model default.
            """
            house_raw = ldap_user.attrs.get("schoolHouse")
            houses = Student.House.labels
            if house_raw:
                if house_raw[0] in houses:
                    data["house"] = house_raw[0][0:2].upper()

            year_raw = ldap_user.attrs.get("schoolYear")
            if year_raw:
                years = Student.Year
                data["year"] = years.labels.index(year_raw[0].split(" ")[0])

            prefect_raw = ldap_user.attrs.get("prefect")[0]
            if prefect_raw == "TRUE":
                data["prefect"] = True
            else:
                data["prefect"] = False

            """
            As quidditch is its own object, it needs to be created, then linked
            """
            quidditch_raw = ldap_user.attrs.get("quidditchPlayer")
            if quidditch_raw:
                if quidditch_raw[0] == "TRUE":
                    try:
                        temp_profile2 = user.student.quidditchplayer
                        print(temp_profile2)
                    except Exception:
                        temp_profile2 = QuidditchPlayer.objects.create(
                            student=user.student
                        )
                        temp_profile2.save()
                    # user.quidditchplayer.save()

            """
            Set all attributes and save the object
            """
            for key, value in data.items():
                if value:
                    setattr(user.student, key, value)
            user.student.save()

        elif account_type == "staff":
            # Add to All Staff Group
            all_staff_group = Group.objects.get(name="All Staff")
            user.groups.add(all_staff_group)
            try:
                temp_profile = user.staff
            except Exception:
                temp_profile = Staff.objects.create(user=user)

            head_of_house_raw = ldap_user.attrs.get("headofHouse")
            if head_of_house_raw:
                data["is_head_of_house"] = True
                user.groups.add(Group.objects.get(name="Head of House"))

            for key, value in data.items():
                if value:
                    setattr(user.staff, key, value)
            user.staff.save()
    else:
        pass


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

        try:
            """
            Student creation may need dependent Quidditch Object as well
            This is created after the initial student object is created since
            Quidditch is 1-2-1 relation and will error if object does not exist
            """
            account_type = instance.ldap_user.attrs.get("employeeType")[0].lower()
            data: dict = {}

            if account_type == "student":
                # Add to All Students Group
                all_students_group = Group.objects.get(name="All Students")
                instance.groups.add(all_students_group)

                # Create Actual Student Object with attributes
                profile = Student.objects.create(user=instance)

                """
                Initial  Student attributes are School House, School Year, and 
                Prefect status. If a value from LDAP is supplied then we use that,
                otherwise we fall back to the model default value for the
                attribute. We also create a linked Quidditch object as needed.
                LDAP does not currently store the granular quidditch attributes
                at this time so those values  fall-back to model default.
                """
                house_raw = instance.ldap_user.attrs.get("schoolHouse")
                houses = Student.House.labels
                if house_raw[0] in houses:
                    data["house"] = house_raw[0][0:2].upper()

                year_raw = instance.ldap_user.attrs.get("schoolYear")
                years = Student.Year
                data["year"] = years.labels.index(year_raw[0].split(" ")[0])

                prefect_raw = instance.ldap_user.attrs.get("prefect")[0]
                if prefect_raw == "TRUE":
                    data["prefect"] = True
                else:
                    data["prefect"] = False

                quidditch_raw = instance.ldap_user.attrs.get("quidditchPlayer")

                """
                Student object must be saved here before Quidditch Object is 
                created
                """
                for key, value in data.items():
                    if value:
                        setattr(profile, key, value)
                profile.save()

                if quidditch_raw[0] == "TRUE":
                    try:
                        temp_profile = profile.quidditchplayer
                    except Exception:
                        temp_profile = QuidditchPlayer.objects.create(student=profile)
                    temp_profile.save()

            elif account_type == "staff":
                # Add to All Staff Group
                all_staff_group = Group.objects.get(name="All Staff")
                instance.groups.add(all_staff_group)

                # Create Actual Student Object with attributes
                profile = Staff.objects.create(user=instance)

                head_of_house_raw = instance.ldap_user.attrs.get("headofHouse")
                if head_of_house_raw:
                    data["is_head_of_house"] = True
                    instance.groups.add(Group.objects.get(name="Head of House"))

                for key, value in data.items():
                    if value:
                        setattr(profile, key, value)
                profile.save()

            elif account_type == "parent":
                # Add to All Parent Group
                all_parents_group = Group.objects.get(name="All Parents")
                instance.groups.add(all_parents_group)

        except AttributeError:
            print("Created User via non-ldap route before ldap user exists")
            pass
