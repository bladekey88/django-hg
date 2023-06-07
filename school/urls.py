from django.urls import path
from . import views

app_name = "school"

urlpatterns = [
    path("", views.home, name="home"),
    path("student/", views.student_main, name="student_main"),
    path("staff/", views.staff, name="staff_main"),
    path("parent/", views.parent, name="parent_main"),
    path(
        "parent/children",
        views.ParentChild.as_view(),
        name="parent_childlist",
    ),
    path(
        "parent/child/<int:pk>/",
        views.Child.as_view(),
        name="children",
    ),
]
