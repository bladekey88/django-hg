from django.contrib.auth import get_user_model
from django.test import TestCase


class UsersManagersTests(TestCase):
    # Create your tests here.
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
