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
        "email",
        "get_house",
        "is_active",
        "is_staff",
        "is_superuser",
        "last_login",
        "date_joined",
    )

    @admin.display(description="Full Name", ordering="student__last_name")
    def get_fullname(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}"

    @admin.display(description="House", ordering="student__house")
    def get_house(self, obj):
        return obj.student.house

    list_filter = (
        "is_staff",
        "is_active",
        "date_joined",
        "last_login",
        "student__house",
    )
    fieldsets = (
        (
            "Core Attributes",
            {
                "fields": (
                    "idnumber",
                    "email",
                    "password",
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
    search_fields = ("email", "idnumber", "student__house")
    ordering = ("email",)


admin.site.register(CustomUser, CustomUserAdmin)
