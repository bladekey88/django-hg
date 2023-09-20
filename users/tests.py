from django.contrib.auth import get_user_model
from django.test import TestCase
from django.contrib.auth.models import Group
from .models import Student
from django.core.exceptions import ValidationError


class UsersManagersTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        groups = [
            "All Users",
            "All Students",
            "All Staff",
            "All Parents",
            "Head of House",
        ]
        for group in groups:
            Group.objects.create(name=group)

    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            email="test@hogwarts.wiz", idnumber="923029382", password="laptop"
        )
        self.assertEqual(user.email, "test@hogwarts.wiz")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        try:
            # username is None for the AbstractUser option
            # username does not exist for the AbstractBaseUser option
            self.assertIsNone(user.username)
        except AttributeError:
            pass
        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(TypeError):
            User.objects.create_user(email="")
        with self.assertRaises(TypeError):
            User.objects.create_user(idnumber="")
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", idnumber="", password="foo")
        with self.assertRaises(ValueError):
            User.objects.create_user(
                idnumber="", email="test@hogwarts.wiz", password="foo"
            )
        with self.assertRaises(ValueError):
            User.objects.create_user(idnumber="12334", email="", password="foo")

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            email="super@user.com", idnumber="923029382", password="foo"
        )
        self.assertEqual(admin_user.email, "super@user.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        try:
            # username is None for the AbstractUser option
            # username does not exist for the AbstractBaseUser option
            self.assertIsNone(admin_user.username)
        except AttributeError:
            pass
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="super@user.com",
                password="foo",
                idnumber="923029382",
                is_superuser=False,
            )

    def test_create_student(self):
        User = get_user_model()
        user = User.objects.create_user(
            email="test@hogwarts.wiz",
            idnumber="923029382",
            password="password",
        )
        student = Student.objects.create(user=user)
        self.assertTrue(user.is_student)
        self.assertFalse(user.is_staff)
        self.assertTrue(student.is_unsorted)
        self.assertFalse(student.is_sorted)
        self.assertFalse(student.is_owl_student)
        self.assertFalse(student.is_newt_student)
        self.assertIsNone(student._validate_prefect())
        self.assertIsNone(student._validate_student_eligiblity())
        self.assertEqual(student.house, Student.House.UNSORTED)
        self.assertEqual(student.year, Student.Year.UNKNOWN)

    def test_create_student_house(self):
        User = get_user_model()
        user = User.objects.create_user(
            email="test@hogwarts.wiz",
            idnumber="923029382",
            password="password",
        )
        student = Student.objects.create(user=user, house="GR")
        self.assertTrue(user.is_student)
        self.assertTrue(student.is_sorted)
        self.assertFalse(student.is_unsorted)
        self.assertEqual(student.house, Student.House.GRYFFINDOR)
        self.assertEqual(student.house, "GR")
        self.assertEqual(student.get_house_display(), "Gryffindor")
        self.assertEqual(student.year, Student.Year.UNKNOWN)

    def test_create_student_year(self):
        User = get_user_model()
        user = User.objects.create_user(
            email="test@hogwarts.wiz",
            idnumber="923029382",
            password="password",
        )
        student = Student.objects.create(user=user, year=5)
        self.assertTrue(user.is_student)
        self.assertFalse(student.is_sorted)
        self.assertTrue(student.is_unsorted)
        self.assertTrue(student.is_owl_student)
        self.assertFalse(student.is_newt_student)
        self.assertEqual(student.house, Student.House.UNSORTED)
        self.assertEqual(student.year, 5)
        self.assertEqual(student.year, Student.Year.FIFTH)
        self.assertEqual(student.get_year_display(), "Fifth")

    def test_create_student_older_year(self):
        User = get_user_model()
        user = User.objects.create_user(
            email="test@hogwarts.wiz",
            idnumber="923029382",
            password="password",
        )
        student = Student.objects.create(user=user, house="GR", year=6)
        self.assertTrue(user.is_student)
        self.assertTrue(student.is_sorted)
        self.assertFalse(student.is_unsorted)
        self.assertFalse(student.is_owl_student)
        self.assertTrue(student.is_newt_student)

    def test_prefect(self):
        User = get_user_model()
        user = User.objects.create_user(
            email="test@hogwarts.wiz",
            idnumber="923029382",
            password="password",
        )
        student = Student.objects.create(user=user, house="GR", year=6, prefect=True)
        self.assertTrue(user.is_student)
        self.assertTrue(student.prefect)
        self.assertIsNone(student._validate_prefect())
        with self.assertRaises(ValidationError):
            student.year = 4
            student.clean()
            student.save()
        with self.assertRaises(ValidationError):
            student.year = 5
            student.house = student.House.UNSORTED
            student.clean()
            student.save()

    def test_student_group_membership(self):
        User = get_user_model()
        user = User.objects.create_user(
            email="test@hogwarts.wiz",
            idnumber="923029382",
            password="password",
        )

        all_user_group = Group.objects.get(name="All Users")
        all_student_group = Group.objects.get(name="All Students")
        all_staff_group = Group.objects.get(name="All Staff")
        self.assertTrue(user.groups.filter(name=all_user_group.name).exists())
        self.assertFalse(user.groups.filter(name=all_student_group.name).exists())
        self.assertFalse(user.groups.filter(name=all_staff_group.name).exists())
        student = Student.objects.create(user=user, house="SL", year=3)
        self.assertTrue(user.groups.filter(name=all_user_group.name).exists())
        self.assertTrue(user.groups.filter(name=all_student_group.name).exists())
        self.assertFalse(user.groups.filter(name=all_staff_group.name).exists())
        student.delete()
        self.assertTrue(user.groups.filter(name=all_user_group.name).exists())
        self.assertFalse(user.groups.filter(name=all_student_group.name).exists())
        self.assertFalse(user.groups.filter(name=all_staff_group.name).exists())
