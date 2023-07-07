from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import (
    PermissionRequiredMixin,
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.http import HttpResponse, HttpResponseForbidden
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView
from users.models import Parent, CustomUser
from school.models import BasicCourse
from django.urls import reverse_lazy


# Create your views here.
@login_required
def student_main(request):
    if not request.user.is_student() and not request.user.is_superuser:
        return redirect("school:home")
    else:
        return HttpResponse(f"Welcome Student {request.user}")


@login_required
def staff(request):
    if not request.user.is_school_staff() and not request.user.is_superuser:
        return redirect("school:home")
    else:
        return HttpResponse(f"Welcome Staff {request.user}")


class ParentLandingView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Parent
    permission_required = [
        "users.view_parent",
    ]
    template_name = "users/parents_landing.html"

    def handle_no_permission(self):
        return redirect("school:home")


class ParentChild(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Parent
    permission_required = [
        "users.view_parent",
    ]
    template_name = "users/parent_list.html"

    def get_queryset(self):
        return (
            Parent.objects.get(user=self.request.user).children.all().order_by("-year")
        )


class Child(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = CustomUser
    permission_required = ["users.view_student", "users.view_parent"]

    slug_field = "uid"
    slug_url_kwarg = "uid"
    template_name = "users/children.html"

    def get_object(self):
        if self.request.user.is_superuser:
            return CustomUser.objects.get(id=self.kwargs.get("pk"))
        else:
            user = CustomUser.objects.get(id=self.kwargs.get("pk"))
            current_user = Parent.objects.get(user=self.request.user)
            current_user_children = current_user.children.all()
            if user.uid in current_user_children.values_list(
                "user__uid",
                flat=True,
            ):
                return user
            else:
                return get_object_or_404(CustomUser, pk=-1)


class CoursesView(UserPassesTestMixin, ListView):
    model = BasicCourse
    template_name = "school/course_list.html"

    def test_func(self):
        return self.request.user.is_school_staff() or self.request.user.is_superuser


class CourseView(PermissionRequiredMixin, UserPassesTestMixin, DetailView):
    permission_required = ["school.view_basiccourse"]
    model = BasicCourse
    template_name = "school/course_detail.html"
    slug_url_kwarg = "slug"

    def test_func(self):
        return self.request.user.is_school_staff() or self.request.user.is_superuser


class CourseAdd(PermissionRequiredMixin, CreateView):
    permission_required = ["school.add_basiccourse"]
    model = BasicCourse
    fields = [
        "name",
        "course_code",
        "course_type",
        "required",
        "description",
    ]
    template_name = "school/course_add.html"


class CourseDelete(PermissionRequiredMixin, DeleteView):
    permission_required = [
        "school.delete_basiccourse",
        "school.delete_basicclass",
    ]
    permission_denied_message = "Access Forbidden"
    model = BasicCourse
    template_name = "school/course_detail.html"
    success_url = reverse_lazy("school:courses_view")


def home(request):
    if request.user.is_anonymous:
        return HttpResponseForbidden("Access Denied")
    if request.user.is_student():
        return redirect("school:student_main")
    elif request.user.is_school_staff():
        return redirect("school:staff_main")
    elif request.user.is_parent():
        return redirect("school:parent_main")
    else:
        return HttpResponse(f"{request.user} has a non-standard account")
