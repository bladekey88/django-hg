from django.dispatch import receiver
import django_auth_ldap.backend
from users.models import Student, CustomUser, QuidditchPlayer
from django.db.models.signals import post_save
from django.contrib.auth.models import Group


def populate_user_profile(sender, user, ldap_user, **kwargs):
    """
    Signal Handler that determines what Profile Type is needed and populates
    the attributes appropriately. This will get called after authentication
    against LDAP and core CustomUser/user attributes are mapped,
    """

    if CustomUser.objects.filter(uid=user.uid).exists():
        temp_profile = None
        data = {}
        account_type = ldap_user.attrs["employeeType"][0]
        if account_type.lower() == "student":
            try:
                temp_profile = user.student
            except Exception:
                temp_profile = Student.objects.create(user=user)
            house_raw = ldap_user.attrs.get("schoolHouse")
            houses = Student.House.labels
            if house_raw[0] in houses:
                data["house"] = house_raw[0][0:2].upper()
            year_raw = ldap_user.attrs.get("schoolYear")
            years = Student.Year
            data["year"] = years.labels.index(year_raw[0].split(" ")[0])
            quidditch_raw = ldap_user.attrs.get("quidditchPlayer")
            prefect_raw = ldap_user.attrs.get("prefect")[0]
            if prefect_raw == "TRUE":
                data["prefect"] = True
            else:
                data["prefect"] = False
            if quidditch_raw:
                if quidditch_raw[0] == "TRUE":
                    try:
                        temp_profile2 = user.student.quidditchplayer
                        print("halt")
                    except Exception:
                        temp_profile2 = QuidditchPlayer.objects.create(
                            student=user.student
                        )
                    temp_profile2.save()
                    # user.quidditchplayer.save()
            for key, value in data.items():
                if value:
                    setattr(user.student, key, value)
            user.student.save()
        elif account_type.lower() == "staff":
            # Add to All Staff Group
            all_staff_group = Group.objects.get(name="All Staff")
            user.groups.add(all_staff_group)

    else:
        pass  # This means  User is logging in first time so create_user_profile signal will handle profile data


django_auth_ldap.backend.populate_user.connect(populate_user_profile)


#######################
# USER FIRST TIME LOGIN
#######################
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Add to All Users
        all_users_group = Group.objects.get(name="All Users")
        instance.groups.add(all_users_group)
        try:
            if instance.ldap_user.attrs.get("employeeType")[0].lower() == "student":
                # Add to All Students Group
                all_students_group = Group.objects.get(name="All Students")
                instance.groups.add(all_students_group)

                # Create Profile Instance
                profile = Student.objects.create(user=instance)
                data = {}
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
                print(instance.ldap_user)
                for key, value in data.items():
                    if value:
                        setattr(profile, key, value)
                profile.save()
                if quidditch_raw[0] == "TRUE":
                    try:
                        temp_profile = profile.quidditchplayer
                        print("halt")
                    except Exception:
                        temp_profile = QuidditchPlayer.objects.create(student=profile)
                    temp_profile.save()

            elif instance.ldap_user.attrs.get("employeeType")[0].lower() == "staff":
                # Add to All Students Group
                all_staff_group = Group.objects.get(name="All Staff")
                instance.groups.add(all_staff_group)
            else:
                pass
        except AttributeError:
            print("Create User via interface not ldap before ldap user is synced")
            pass


# @receiver(populate_user, sender=LDAPBackend)
# def ldap_auth_handler(user, ldap_user, **kwargs):
#     """
#     Signal Handler that determines what Profile Type is needed and populates
#     the attributes appropriately. This will get called after authentication
#     against LDAP and core CustomUser/user attributes are mapped,
#     """

#     # Get attribute
#     data = dict()
#     account_type = ldap_user.attrs["employeeType"][0]
#     user.save()

#     if account_type.lower() == "student":
#         data["house"] = ldap_user.attrs.get("schoolHouse")
#         data["year"] = ldap_user.attrs.get("schoolYear")

#         houses = [x[0] for x in Student.HOUSE_CHOICES]

#         if data["house"][0][0:2].upper() in houses:
#             data["house"] = data["house"][0][0:2].upper()
#         # data["year"] = data["year"][0][0 : data["year"][0].find(" ")].upper()
#         # data["year"] = int(parse(data["year"]))

#         student = Student.objects.create(user=user)

#         for key, value in data.items():
#             if value:
#                 setattr(student, key, value[0].encode("utf-8").decode())
#         student.save()
