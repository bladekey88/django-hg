from typing import Any, Optional
from django.db import models
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import (
    PermissionRequiredMixin,
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from users.models import Parent, CustomUser
from school.models import BasicCourse, BasicClass
from django.urls import reverse_lazy
from school.forms import CourseUpdateForm, ClassAddForm


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


class CoursesView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = BasicCourse
    template_name = "school/course_list.html"

    # Use UserPassesTestMixin here rather than perm check
    # as Students also have that perm in their group
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
        "owner",
    ]
    template_name = "school/course_add.html"
    raise_exception = True
    success_message = "Course created successfully."

    def form_valid(self, form):
        if not form.instance.owner:
            form.instance.owner = self.request.user
        return super().form_valid(form)


class CourseEdit(PermissionRequiredMixin, UserPassesTestMixin, UpdateView):
    permission_required = [
        "school.change_basiccourse",
    ]
    model = BasicCourse
    template_name = "school/course_edit.html"
    form_class = CourseUpdateForm

    def test_func(self):
        course = self.get_object()
        if self.request.user == course.owner.user:
            return True
        elif (
            self.request.user.is_superuser
            or self.request.user.groups.filter(name="Head of House").exists()
        ):
            return True


class CourseDelete(PermissionRequiredMixin, DeleteView):
    permission_required = [
        "school.delete_basiccourse",
        "school.delete_basicclass",
    ]
    permission_denied_message = "Access Forbidden"
    model = BasicCourse
    template_name = "school/course_delete.html"
    success_url = reverse_lazy("school:courses_view")


# Class Section
class ClassesView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = BasicClass
    template_name = "school/class_list_all.html"

    def test_func(self):
        return self.request.user.is_school_staff() or self.request.user.is_superuser


class ClassView(PermissionRequiredMixin, UserPassesTestMixin, DetailView):
    permission_required = ["school.view_basicclass"]
    model = BasicClass
    template_name = "school/class_detail.html"
    slug_url_kwarg = "class_slug"

    def test_func(self):
        return self.request.user.is_school_staff() or self.request.user.is_superuser


class ClassAdd(PermissionRequiredMixin, CreateView):
    permission_required = ["school.view_basicclass"]
    model = BasicClass
    form_class = ClassAddForm
    template_name = "school/class_add.html"
    raise_exception = True
    success_message = "Class created successfully."

    def get_context_data(self, **kwargs):
        context = super(ClassAdd, self).get_context_data(**kwargs)
        context["slug"] = self.kwargs["slug"]
        return context

    def form_valid(self, form):
        form.instance.course = BasicCourse.objects.get(slug=self.kwargs["slug"])
        form.save()
        return super(ClassAdd, self).form_valid(form)


class ClassDelete(PermissionRequiredMixin, DeleteView):
    permission_required = [
        "school.delete_basicclass",
    ]
    permission_denied_message = "Access Forbidden"
    model = BasicClass
    template_name = "school/class_delete.html"
    slug_url_kwarg = "class_slug"

    def get_success_url(self):
        course_id = self.kwargs["slug"]
        return reverse_lazy("school:course_detail", kwargs={"slug": course_id})


# Homepage
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
