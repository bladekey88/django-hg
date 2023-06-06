from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Student, QuidditchPlayer, Staff, Parent
from .forms import CustomUserChangeForm, CustomUserCreationForm
from school.models import BasicCourse, BasicClass


# Register your models here.
class StudentInline(admin.TabularInline):
    model = Student
    verbose_name_plural = "Student"


class BasicClassInline(admin.TabularInline):
    model = BasicClass.student.through
    verbose_name = "Class"
    verbose_name_plural = "Classes"
    extra = 0


class BasicCourseInline(admin.TabularInline):
    model = BasicCourse
    verbose_name = "Course I Own"
    verbose_name_plural = "Courses I Own"
    max_num = 10
    extra = 0
    can_delete = False
    empty_value_display = "N/A"
    readonly_fields = [
        "course_code",
        "course_type",
        "required",
    ]


class QuidditchInline(admin.TabularInline):
    model = QuidditchPlayer
    fields = [
        "team_member_type",
        "team_position",
        "is_captain",
        "is_suspended",
    ]
    extra = 0


class StaffInline(admin.TabularInline):
    model = Staff
    verbose_name = "Staff"


class ParentInline(admin.TabularInline):
    model = Parent.children.through
    verbose_name = "Parent"
    extra = 0
    can_delete = False


class QuidditchPlayerAdmin(admin.ModelAdmin):
    model = QuidditchPlayer
    verbose_name = "Quidditch Player"
    verbose_name_plural = "Quidditch Players"
    list_display = (
        "get_student",
        "get_house",
        "get_year",
        "team_member_type",
        "team_position",
        "is_captain",
        "is_suspended",
    )

    list_filter = [
        "student__house",
        "student__year",
        "team_member_type",
        "team_position",
        "is_captain",
        "is_suspended",
    ]

    search_fields = [
        "student__user__idnumber",
        "student__user__first_name",
        "student__user__last_name",
        "student__user__common_name",
        "student__user__uid",
        "student__user__email",
    ]

    @admin.display(description="Student", ordering="student__user__last_name")
    def get_student(self, obj):
        return obj.student.user.full_common_name()

    @admin.display(
        description="House",
        ordering="student__house",
    )
    def get_house(self, obj):
        return obj.student.get_house_display()

    @admin.display(description="Year", ordering="student__year")
    def get_year(self, obj):
        return f" {obj.student.get_year_display()} Year"

    ordering = ["student__house", "-is_captain", "student__user__last_name"]

    fieldsets = (
        (
            "Student Information",
            {
                "fields": ("student",),
                "description": """ If a student does not appear in the list,
                                    it is likely that the user profile has not
                                    been enabled as as student. Navigate to the
                                    users screen and associate a
                                    profile with their account. """,
            },
        ),
        (
            "Player Position",
            {
                "fields": (
                    "team_member_type",
                    "team_position",
                ),
            },
        ),
        (
            "Team Information",
            {
                "fields": (
                    "is_captain",
                    "is_suspended",
                ),
            },
        ),
    )


class CustomUserAdmin(UserAdmin):
    inlines = [StudentInline, StaffInline]
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
        "get_staff_role",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    )

    @admin.display(description="Staff Role")
    def get_staff_role(self, obj):
        return obj.staff.get_staff_type_display()

    @admin.display(description="Full Name", ordering="last_name")
    def get_fullname(self, obj):
        ln = obj.last_name
        fn = obj.first_name
        cn = obj.common_name
        if obj.middle_name:
            mn = obj.middle_name[0]
            return f"{ln}, {fn}{mn} ({cn})"
        else:
            return f"{ln}, {fn} ({cn})"

    @admin.display(
        description="House",
        ordering="student__house",
    )
    def get_house(self, obj):
        return obj.student.get_house_display()

    @admin.display(description="Year", ordering="student__year")
    def get_year(self, obj):
        return f"{obj.student.get_year_display()} Year"

    list_filter = (
        "is_staff",
        "is_active",
        "date_joined",
        "last_login",
        "student__house",
        "student__year",
        "student__prefect",
        "staff__staff_type",
        "sex",
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
                    "sex",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_active",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important Dates", {"fields": ("date_joined", "last_login")}),
    )
    add_fieldsets = (
        (
            "None",
            {
                "classes": ("wide",),
                "fields": (
                    "idnumber",
                    "uid",
                    "email",
                    "title",
                    "first_name",
                    "last_name",
                    "common_name",
                    "sex",
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
    readonly_fields = ["get_fullname"]
    ordering = ("uid",)


class StudentAdmin(admin.ModelAdmin):
    inlines = [QuidditchInline, ParentInline, BasicClassInline]

    @admin.display(
        description="Student",
        ordering="user__last_name",
    )
    def get_full_name(self, obj):
        return obj.user.full_name(True, True)

    @admin.display(description="First Name")
    def get_first_name(self, obj):
        return obj.user.common_name

    @admin.display(description="Last Name")
    def get_last_name(self, obj):
        return obj.user.last_name

    @admin.display(
        description="Student ID Number",
    )
    def get_idnumber(self, obj):
        return obj.user.idnumber

    @admin.display(description="OWL Student")
    def get_owl(self, obj):
        return obj.is_owl_student()

    @admin.display(description="NEWT Student")
    def get_newt(self, obj):
        return obj.is_newt_student()

    @admin.display(description="Quidditch Player")
    def get_quidditch(self, obj):
        return obj.quidditchplayer.get_team_member_type_display()

    readonly_fields = [
        "get_owl",
        "get_newt",
        "get_quidditch",
    ]

    search_fields = [
        "user__uid",
        "user__last_name",
        "user__first_name",
        "user__middle_name",
        "user__common_name",
        "user__email",
    ]
    list_display = [
        "get_idnumber",
        "get_first_name",
        "get_last_name",
        "get_full_name",
        "house",
        "year",
        "prefect",
    ]
    list_filter = [
        "house",
        "year",
        "prefect",
    ]
    ordering = (
        "user__last_name",
        "user__first_name",
    )


class ParentAdmin(admin.ModelAdmin):
    filter_horizontal = (
        "children",
        "related_parent",
    )

    # Method only show users for 'User' dropdown where they
    # do not exist already in the Student or Staff Objects.
    # This applies to both add form and change form.
    def get_form(self, request, obj=None, **kwargs):
        form = super(ParentAdmin, self).get_form(request, obj, **kwargs)

        # We only need to render the change when they have the change
        # permission. Otherwise for readonly view we can ignore and
        # avoid running the query.
        if "users.change_parent" in request.user.get_all_permissions():
            filters = [
                x.uid
                for x in CustomUser.objects.all()
                if not x.is_student() and not x.is_school_staff()
            ]
            form.base_fields["user"].queryset = CustomUser.objects.filter(
                uid__in=filters
            )
        return form

    # This method removes the object user from the related parent selection
    def render_change_form(self, request, context, *args, **kwargs):
        if "users.change_parent" in request.user.get_all_permissions():
            context["adminform"].form.fields[
                "related_parent"
            ].queryset = Parent.objects.exclude(id__exact=context["object_id"])
        return super(ParentAdmin, self).render_change_form(
            request,
            context,
            *args,
            **kwargs,
        )

    @admin.display(
        description="Parent",
        ordering="user__last_name",
    )
    def get_full_name(self, obj):
        return f"{obj.user.title} {obj.user.full_name(True, False)}"

    @admin.display(description="First Name")
    def get_first_name(self, obj):
        return obj.user.common_name

    @admin.display(description="Last Name")
    def get_last_name(self, obj):
        return obj.user.last_name

    @admin.display(
        description="ID Number",
    )
    def get_idnumber(self, obj):
        return obj.user.idnumber

    @admin.display(description="Number of Children")
    def get_number_of_children(self, obj):
        return obj.children.count()

    @admin.display(description="Linked to Parent")
    def get_related_parent(self, obj):
        return obj.get_related_parent()

    list_display = [
        "get_idnumber",
        "get_full_name",
        "get_number_of_children",
        "get_related_parent",
    ]

    search_fields = [
        "user__uid",
        "user__last_name",
        "user__first_name",
        "user__middle_name",
        "user__common_name",
        "user__email",
    ]

    ordering = [
        "user__last_name",
        "user__first_name",
    ]


class StaffAdmin(admin.ModelAdmin):
    @admin.display(
        description="Staff Member",
        ordering="user__last_name",
    )
    def get_full_name(self, obj):
        return f"{obj.user.title} {obj.user.full_name(True, False)}"

    @admin.display(description="First Name")
    def get_first_name(self, obj):
        return obj.user.first_name

    @admin.display(description="Last Name")
    def get_last_name(self, obj):
        return obj.user.last_name

    @admin.display(
        description="ID Number",
    )
    def get_idnumber(self, obj):
        return obj.user.idnumber

    @admin.display(description="Title")
    def get_title(self, obj):
        return obj.user.title

    inlines = [BasicCourseInline]
    list_display = [
        "get_idnumber",
        "get_title",
        "get_first_name",
        "get_last_name",
        "get_full_name",
        "staff_type",
        "is_head_of_house",
    ]
    list_filter = [
        "staff_type",
        "is_head_of_house",
    ]
    search_fields = [
        "user__uid",
        "user__last_name",
        "user__first_name",
        "user__middle_name",
        "user__common_name",
        "user__email",
    ]
    ordering = [
        "user__last_name",
        "user__first_name",
    ]


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(QuidditchPlayer, QuidditchPlayerAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Staff, StaffAdmin)
admin.site.register(Parent, ParentAdmin)
