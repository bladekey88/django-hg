from typing import Optional
from django.contrib import admin
from django.http.request import HttpRequest
from .models import BasicCourse, BasicClass, SchoolYear, Enrolment, CourseCategory

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

    list_per_page = 20
    empty_value_display = "<No Value>"
    list_display = [
        "name",
        "course_code",
        "course_type",
        "category",
        "required",
        "get_description",
        "owner",
    ]

    list_filter = [
        "course_type",
        "category",
        "required",
        "owner",
    ]
    search_fields = [
        "name",
        "course_code",
    ]

    prepopulated_fields = {
        "slug": ("course_code",),
    }

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(owner=request.user.staff)
        return qs

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


class EnrolmentInline(admin.TabularInline):
    model = Enrolment
    verbose_name_plural = "Enrolments"


class EnrolmentAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "basic_class",
        "created_date",
        "modified_date",
        "student_class_status",
    ]

    list_filter = [
        "created_date",
        "modified_date",
        "student_class_status",
    ]

    readonly_fields = [
        "created_date",
        "modified_date",
    ]

    search_fields = [
        "student__user__last_name",
        "basic_class__name",
    ]


class BasicClassAdmin(admin.ModelAdmin):
    inlines = [EnrolmentInline]
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
        "class_code",
        "get_class_code",
        "course",
        "get_student_exist",
    ]

    search_fields = [
        "name",
        "class_code",
    ]
    list_filter = ["course__category", "teacher"]
    ordering = ["name"]


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


class BasicCourseInline(admin.TabularInline):
    fields = [
        "name",
        "course_code",
        "course_type",
        "required",
        "owner",
    ]
    model = BasicCourse
    can_delete = False
    extra = 0

    def has_add_permission(self, request, obj=None) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False


class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "code"]
    search_fields = ["name"]
    inlines = [BasicCourseInline]


admin.site.register(BasicCourse, BasicCourseAdmin)
admin.site.register(BasicClass, BasicClassAdmin)
admin.site.register(SchoolYear, SchoolYearAdmin)
admin.site.register(Enrolment, EnrolmentAdmin)
admin.site.register(CourseCategory, CourseCategoryAdmin)
