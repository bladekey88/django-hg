from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Student
from .forms import CustomUserChangeForm, CustomUserCreationForm


# Register your models here.
class StudentInline(admin.StackedInline):
    model = Student
    can_delete = False
    verbose_name_plural = "Student"


class CustomUserAdmin(UserAdmin):
    inlines = [StudentInline]
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = (
        "idnumber",
        "get_fullname",
        "uid",
        "email",
        "get_house",
        "get_year",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    )

    @admin.display(description="Full Name", ordering="last_name")
    def get_fullname(self, obj):
        if obj.middle_name:
            return f"{obj.last_name}, {obj.first_name} {obj.middle_name[0]} ({obj.common_name})"
        else:
            return f"{obj.last_name}, {obj.first_name} ({obj.common_name})"

    @admin.display(
        description="House",
        ordering="student__house",
    )
    def get_house(self, obj):
        return obj.student.house

    @admin.display(description="Year", ordering="student__year")
    def get_year(self, obj):
        return obj.student.year

    list_filter = (
        "is_staff",
        "is_active",
        "date_joined",
        "last_login",
        "student__house",
        "student__year",
    )
    fieldsets = (
        (
            "Core Attributes",
            {
                "fields": (
                    "idnumber",
                    "email",
                    "uid",
                    "password",
                    "title",
                    "first_name",
                    "last_name",
                    "common_name",
                    "middle_name",
                )
            },
        ),
        (
            "Permissions",
            {"fields": ("is_staff", "is_active", "groups", "user_permissions")},
        ),
        ("Important Dates", {"fields": ("date_joined", "last_login")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "idnumber",
                    "email",
                    "uid",
                    "title",
                    "first_name",
                    "last_name",
                    "common_name",
                    "middle_name",
                    "password1",
                    "password2",
                    "date_joined",
                    "is_staff",
                    "is_active",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )
    search_fields = (
        "email",
        "uid",
        "idnumber",
        "common_name",
        "first_name",
        "last_name",
    )
    ordering = ("uid",)


admin.site.register(CustomUser, CustomUserAdmin)
