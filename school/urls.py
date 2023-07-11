from django.urls import path
from . import views


app_name = "school"

urlpatterns = [
    path("", views.home, name="home"),
    path("student/", views.student_main, name="student_main"),
    path("staff/", views.Staff.as_view(), name="staff_main"),
    # Course Section
    path(
        "staff/courses/",
        views.CoursesView.as_view(),
        name="courses_view",
    ),
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
        views.CourseView.as_view(),
        name="course_detail",
    ),
    path(
        "staff/courses/<slug:slug>/edit/",
        views.CourseEdit.as_view(),
        name="course_edit",
    ),
    path(
        "staff/courses/<slug:slug>/delete/",
        views.CourseDelete.as_view(),
        name="course_delete",
    ),
    # Classes Section (as a subset of courses)
    path(
        "staff/courses/<slug:slug>/classes/<slug:class_slug>",
        views.ClassView.as_view(),
        name="class_detail",
    ),
    path(
        "staff/courses/<slug:slug>/classes/add-class/",
        views.ClassAdd.as_view(),
        name="class_add",
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
        "parent/children/<int:pk>/",
        views.Child.as_view(),
        name="children",
    ),
]
