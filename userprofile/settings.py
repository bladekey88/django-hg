"""
Django settings for userprofile project.

Generated by 'django-admin startproject' using Django 4.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
from django_auth_ldap.config import LDAPSearch, LDAPGroupQuery, GroupOfNamesType
import ldap

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-$$+_f^+968zw&tn0n%6$0^g7*!)2g8s7s3dl_^cvu1hl#k(3@="

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1"]


# Application definition

INSTALLED_APPS = [
    "account.apps.AccountConfig",
    "school.apps.SchoolConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "formtools",
    "users.apps.UsersConfig",
    "ldap_sync",
    "crispy_forms",
    "crispy_bootstrap5",
    "debug_toolbar",
    "mail",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "userprofile.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "userprofile.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "django_site",
        "USER": "django",
        "PASSWORD": "laptop",
        "HOST": "127.0.0.1",
        "PORT": "3306",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-GB"
TIME_ZONE = "Europe/London"
USE_I18N = True
USE_TZ = True
USE_L10N = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field


INTERNAL_IPS = [
    "127.0.0.1",
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "users.CustomUser"
FORMAT_MODULE_PATH = "userprofile.formats"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "django_auth_ldap.backend.LDAPBackend",
]


# LDAP Settings
AUTH_LDAP_SERVER_URI = "ldap://hogwarts.wiz"
AUTH_LDAP_BIND_DN = "cn=admin,dc=hogwarts,dc=wiz"
AUTH_LDAP_BIND_PASSWORD = "laptop"
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    "ou=people,dc=hogwarts,dc=wiz", ldap.SCOPE_SUBTREE, "(uid=%(user)s)"  # type: ignore
)

AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "middle_name": "middleName",
    "common_name": "displayName",
    "email": "mail",
    "idnumber": "employeeNumber",
    "student.house": "schoolHouse",
    "title": "title",
    "quidditchplayer.is_player": "quidditchPlayer",
    "uid": "uid",
    "sex": "sex",
    "prefect": "prefect",
}


AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    "ou=groups,dc=hogwarts,dc=wiz", ldap.SCOPE_SUBTREE, "(objectClass=groupOfNames)"
)
AUTH_LDAP_GROUP_TYPE = GroupOfNamesType()

AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    "is_staff": LDAPGroupQuery("cn=all users,ou=openfire,ou=groups,dc=hogwarts,dc=wiz"),
    "is_superuser": LDAPGroupQuery("cn=administrators,ou=groups,dc=hogwarts,dc=wiz"),
}


LOGIN_REDIRECT_URL = "account:dashboard"
LOGIN_URL = "account:login"
LOGOUT_URL = "account:logout"
LOGOUT_REDIRECT_URL = "account:login"
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "mail.hogwarts.wiz"
EMAIL_HOST_USERNAME = "service-portal@hogwarts.wiz"
EMAIL_HOST_PASSWORD = "7freN8hy1988!"
EMAIL_USE_TLS = True
# EMAIL_USE_SSL = True


LDAP_SYNC_URI = AUTH_LDAP_SERVER_URI
LDAP_SYNC_BASE = "ou=people,dc=hogwarts,dc=wiz"
LDAP_SYNC_BASE_USER = AUTH_LDAP_BIND_DN
LDAP_SYNC_BASE_PASS = AUTH_LDAP_BIND_PASSWORD
LDAP_SYNC_USER_FILTER = "(&(objectClass=inetOrgPerson)(objectClass=hogwartsAttributes))"
LDAP_SYNC_USER_ATTRIBUTES = {
    "uid": "uid",
    "mail": "email",
    "givenName": "first_name",
    "sn": "last_name",
    "employeeNumber": "idnumber",
    "title": "title",
    "middleName": "middle_name",
    "displayName": "common_name",
    "sex": "sex",
    "title": "title",
}

SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 60 * 60
SESSION_SAVE_EVERY_REQUEST = True
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
