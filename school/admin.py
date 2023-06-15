from django.contrib import admin
from .models import BasicCourse, BasicClass, SchoolYear

# Register your models here.


class BasicCourseAdmin(admin.ModelAdmin):
    @admin.display(description="Course Description", empty_value="N/A")
    def get_description(self, obj):
        short_description = obj.description
        if short_description:
            if len(short_description) > 100:
                return f"{short_description[:100]}..."
            else:
                return f"{short_description}"

    empty_value_display = "-"
    list_display = [
        "name",
        "course_code",
        "course_type",
        "required",
        "get_description",
        "owner",
    ]

    list_filter = [
        "course_type",
        "required",
        "owner",
    ]
    search_fields = [
        "name",
        "course_code",
    ]

    def has_change_permission(self, request, obj=None):
        if obj is not None:
            if request.user.is_superuser:  # type: ignore
                return True
            elif not obj.owner:  # type: ignore
                return True
            else:
                if request.user.id != obj.owner.user.id:  # type: ignore
                    return False
                else:
                    return True


class BasicClassAdmin(admin.ModelAdmin):
    filter_horizontal = (
        "teacher",
        "student",
    )

    @admin.display(
        description="Class Code",
    )
    def get_class_code(self, obj):
        return obj.get_class_code()

    @admin.display(description="Number of Students")
    def get_student_exist(self, obj):
        if obj.student.count() > 0:
            return obj.student.count()
        else:
            return "None"

    list_display = [
        "name",
        "get_class_code",
        "course",
        "get_student_exist",
    ]

    search_fields = [
        "name",
        "class_code",
    ]

    ordering = ["class_code"]


class SchoolYearAdmin(admin.ModelAdmin):
    """Admin View for School Year"""

    list_display = (
        "name",
        "start_year",
        "end_year",
    )
    list_filter = (
        "start_date",
        "end_date",
        "start_year",
        "end_year",
    )

    ordering = (
        "end_year",
        "start_year",
    )


admin.site.register(BasicCourse, BasicCourseAdmin)
admin.site.register(BasicClass, BasicClassAdmin)
admin.site.register(SchoolYear, SchoolYearAdmin)
