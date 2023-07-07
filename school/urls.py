from django.urls import path
from . import views


app_name = "school"

urlpatterns = [
    path("", views.home, name="home"),
    path("student/", views.student_main, name="student_main"),
    path("staff/", views.staff, name="staff_main"),
    path("staff/courses/add-course/", views.CourseAdd.as_view(), name="course_add"),
    path("staff/courses/", views.CoursesView.as_view(), name="courses_view"),
    path(
        "staff/courses/<slug:slug>/",
        views.CourseView.as_view(),
        name="course_detail",
    ),
    path(
        "staff/courses/<slug:slug>/delete/",
        views.CourseDelete.as_view(),
        name="course_delete",
    ),
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
