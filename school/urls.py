from django.urls import path
from . import views


app_name = "school"

urlpatterns = [
    path("", views.home, name="home"),
    # Student Section
    path(
        "student/",
        views.StudentLandingView.as_view(),
        name="student_main",
    ),
    path(
        "student/student/<student>/",
        views.StudentProfileView.as_view(),
        name="student_profile",
    ),
    path(
        "student/houses/",
        views.StudentHouses.as_view(),
        name="student_houses",
    ),
    # Staff Section
    path(
        "staff/",
        views.StaffIndexView.as_view(),
        name="staff_main",
    ),
    path(
        "staff/staff/<staff>/",
        views.StaffProfileView.as_view(),
        name="staff_profile",
    ),
    path(
        "staff/view-students/",
        views.StaffViewStudent.as_view(),
        name="old_staff_view_students",
    ),
    path(
        "school/view-students/house/<house>/",
        views.ViewStudentHouse.as_view(),
        name="student_house",
    ),
    path(
        "school/view-students/a-z/<letter>/",
        views.ViewStudentAlpha.as_view(),
        name="student_a_z",
    ),
    path(
        "school/view-students/year/<year>/",
        views.StaffViewStudentYear.as_view(),
        name="staff_year",
    ),
    # Course Section
    # This needs to be added here to ensure that the slug path does
    # not override this url. This page is not really used directly, but is a
    # useful table list of all the classes
    path(
        "staff/courses/classes/",
        views.ClassesView.as_view(),
        name="classes_view_all",
    ),
    path(
        "staff/courses/add-course/",
        views.CourseAdd.as_view(),
        name="course_add",
    ),
    path(
        "staff/courses/<slug:slug>/",
        views.CourseViewStaff.as_view(),
        name="course_detail_staff",
    ),
    path(
        "staff/courses/<slug:slug>/edit/",
        views.CourseEdit.as_view(),
        name="course_edit",
    ),
    path(
        "school/courses/<slug:slug>/ownership/",
        views.CourseOwnershipChangeView.as_view(),
        name="course_ownership_change",
    ),
    path(
        "staff/courses/<slug:slug>/delete/",
        views.CourseDelete.as_view(),
        name="course_delete",
    ),
    # Classes Section (as a subset of courses)
    path(
        "staff/courses/<slug:slug>/classes/add-class/",
        views.ClassAdd.as_view(),
        name="class_add",
    ),
    path(
        "staff/courses/<slug:slug>/classes/<slug:class_slug>/",
        views.ClassView.as_view(),
        name="class_detail",
    ),
    path(
        "staff/courses/<slug:slug>/classes/<slug:class_slug>/edit/",
        views.ClassEdit.as_view(),
        name="class_edit",
    ),
    path(
        "staff/courses/<slug:slug>/classes/<slug:class_slug>/enrol/",
        views.ClassEnrol.as_view(),
        name="class_enrol",
    ),
    path(
        "staff/courses/<slug:slug>/classes/<slug:class_slug>/delete/",
        views.ClassDelete.as_view(),
        name="class_delete",
    ),
    # Schedule
    path(
        "staff/schedules/",
        views.SchedulesView.as_view(),
        name="schedules_view",
    ),
    path(
        "staff/schedules/add-schedule/",
        views.ScheduleAdd.as_view(),
        name="schedule_add",
    ),
    path(
        "staff/schedules/<slug:slug>/",
        views.ScheduleView.as_view(),
        name="schedule_detail",
    ),
    path(
        "staff/schedules/<slug:slug>/edit/",
        views.ScheduleEdit.as_view(),
        name="schedule_edit",
    ),
    path(
        "staff/schedules/<slug:slug>/delete/",
        views.ScheduleDelete.as_view(),
        name="schedule_delete",
    ),
    # Parent Section
    path(
        "parent/",
        views.ParentLandingView.as_view(),
        name="parent_main",
    ),
    path(
        "parent/children/",
        views.ParentChild.as_view(),
        name="parent_childlist",
    ),
    path(
        "parent/children/<child_user>/",
        views.Child.as_view(),
        name="children",
    ),
    # General School Section
    path(
        "school/courses/",
        views.CourseCategoryView.as_view(),
        name="courses_view_all",
    ),
    path(
        "school/courses/<slug:slug>/",
        views.CourseView.as_view(),
        name="course_detail",
    ),
    path(
        "school/view-students/",
        views.ViewStudents.as_view(),
        name="view_students",
    ),
]
