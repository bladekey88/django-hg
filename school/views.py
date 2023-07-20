from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.mixins import (
    PermissionRequiredMixin,
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseForbidden, Http404
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from users.models import Parent, CustomUser, Student
from school.models import BasicCourse, BasicClass, SchoolYear
from django.urls import reverse_lazy
from school.forms import (
    CourseUpdateForm,
    ClassAddForm,
    ClassUpdateForm,
    ClassEnrolForm,
    ScheduleUpdateForm,
    ScheduleAddForm,
)


# Create your views here.
class StudentLandingView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = ["users.view_student"]
    template_name = "users/staff_landing.html"

    def get(self, request):
        if not request.user.is_student() and not request.user.is_superuser:
            return redirect("school:home")
        else:
            return render(request, self.template_name)


class StudentHouses(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = ["users.view_student"]
    template_name = "users/houses.html"

    def get_context_data(self):
        context = super().get_context_data()
        context["houses"] = Student.House
        return context


class StudentProfile(LoginRequiredMixin, View):
    template_name = "account/profile.html"

    def get(self, request, student):
        try:
            cu = CustomUser.objects.get(uid=student)
            if cu.is_student():
                context = {}
                context["user"] = cu
                return render(request, self.template_name, context=context)
            else:
                raise Http404("Student Not Found")
        except Exception:
            raise Http404("Student Not Found")


class Staff(LoginRequiredMixin, View):
    template_name = "users/staff_landing.html"

    def get(self, request):
        if not request.user.is_school_staff() and not request.user.is_superuser:
            return redirect("school:home")
        else:
            return render(request, self.template_name)


# Inherit as it's the same page
class StaffHouses(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = ["users.view_student", "users.view_staff"]
    template_name = "users/houses.html"

    def get_context_data(self):
        context = super().get_context_data()
        context["houses"] = Student.House
        return context


class StaffHouse(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = ["users.view_student", "users.view_staff"]
    template_name = "users/staff_house.html"

    def get(self, request, house):
        if house.lower() in [e.name.lower() for e in Student.House]:
            output = [e.value for e in Student.House if house.lower() == e.name.lower()]
            qs = (
                Student.objects.filter(house=output[0])
                .all()
                .order_by(
                    "year",
                    "user__first_name",
                )
            )
            context = {}
            context["qs"] = qs
            context["house"] = house
            return render(request, self.template_name, context=context)
        else:
            raise Http404("House does not exist or is not accessible.")


class ParentLandingView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Parent
    permission_required = ["users.view_parent"]
    template_name = "users/parents_landing.html"

    def handle_no_permission(self):
        return redirect("school:home")


class ParentChild(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Parent
    permission_required = ["users.view_parent"]
    template_name = "users/parent_child_list.html"

    def get_queryset(self):
        return (
            Parent.objects.get(user=self.request.user).children.all().order_by("-year")
        )


class Child(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    model = CustomUser
    permission_required = ["users.view_student", "users.view_parent"]

    slug_field = "uid"
    slug_url_kwarg = "uid"
    template_name = "users/parent_child.html"

    def get(self, request, child_user):
        context = {}
        try:
            get_object_or_404(CustomUser, uid=child_user)
            child = CustomUser.objects.get(uid=child_user)
            context["object"] = child
        except ObjectDoesNotExist:
            return get_object_or_404(CustomUser, -1)

        if not request.user.is_superuser:
            parent = Parent.objects.get(user=request.user)
            children_of_parent = parent.children.all()
            if child.uid not in children_of_parent.values_list(
                "user__uid",
                flat=True,
            ):
                return get_object_or_404(CustomUser, uid=None)

        return render(request, template_name=self.template_name, context=context)


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
        if course.owner is None:
            return True
        elif self.request.user == course.owner.user:
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


class ClassEdit(PermissionRequiredMixin, UserPassesTestMixin, UpdateView):
    permission_required = [
        "school.change_basicclass",
    ]
    model = BasicClass
    template_name = "school/class_edit.html"
    form_class = ClassUpdateForm
    slug_url_kwarg = "class_slug"

    def test_func(self):
        school_class = self.get_object()
        teacher_all = school_class.teacher.all()
        output = [teacher.user.id for teacher in teacher_all]
        if self.request.user == school_class.course.owner.user:
            return True
        elif (
            self.request.user.is_superuser
            or self.request.user.groups.filter(name="Head of House").exists()
        ):
            return True
        elif self.request.user.id in output:
            return True


class ClassEnrol(PermissionRequiredMixin, UserPassesTestMixin, UpdateView):
    permission_required = [
        "school.change_basicclass",
        "users.view_student",
    ]
    model = BasicClass
    template_name = "school/class_enrol.html"
    slug_url_kwarg = "class_slug"
    form_class = ClassEnrolForm

    def test_func(self):
        school_class = self.get_object()
        teacher_all = school_class.teacher.all()
        output = [teacher.user.id for teacher in teacher_all]
        if self.request.user.id in output:
            return True
        elif (
            self.request.user.is_superuser
            or self.request.user.groups.filter(name="Head of House").exists()
        ):
            return True


class ClassDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ["school.delete_basicclass"]
    permission_denied_message = "Access Forbidden"
    model = BasicClass
    template_name = "school/class_delete.html"
    slug_url_kwarg = "class_slug"

    def get_success_url(self):
        course_id = self.kwargs["slug"]
        return reverse_lazy("school:course_detail", kwargs={"slug": course_id})


# Schedule Section
class SchedulesView(PermissionRequiredMixin, ListView):
    permission_required = ["school.view_schoolyear"]
    model = SchoolYear
    template_name = "school/schedule_list.html"


class ScheduleView(PermissionRequiredMixin, DetailView):
    permission_required = ["school.view_schoolyear"]
    model = SchoolYear
    template_name = "school/schedule_detail.html"
    slug_url_kwarg = "slug"


class ScheduleAdd(PermissionRequiredMixin, CreateView):
    permission_required = ["school.add_schoolyear"]
    model = SchoolYear
    template_name = "school/schedule_add.html"
    slug_url_kwarg = "slug"
    form_class = ScheduleAddForm


class ScheduleEdit(PermissionRequiredMixin, UpdateView):
    permission_required = ["school.change_schoolyear"]
    model = SchoolYear
    template_name = "school/schedule_edit.html"
    slug_url_kwarg = "slug"
    form_class = ScheduleUpdateForm


class ScheduleDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ["school.delete_schoolyear"]
    model = SchoolYear
    template_name = "school/schedule_delete.html"
    slug_url_kwarg = "slug"

    def get_success_url(self):
        return reverse_lazy("school:schedules_view")


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
