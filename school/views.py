from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.mixins import (
    PermissionRequiredMixin,
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import HttpResponse, Http404
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from users.models import Parent, CustomUser, Student, Staff
from school.models import BasicCourse, BasicClass, SchoolYear, CourseCategory
from django.urls import reverse_lazy
from school.forms import (
    CourseUpdateForm,
    ClassAddForm,
    ClassUpdateForm,
    ClassEnrolForm,
    ScheduleUpdateForm,
    ScheduleAddForm,
)
from django.db.models import Q


# Student Section
class StudentProfileView(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "users/profile_beta.html"
    permission_required = ["users.view_student"]

    def get_siblings(self, student):
        current_student = Student.objects.get(user=student)
        parents = current_student.children_of.all()
        if len(parents) > 0:
            sibling_list = []
            for parent in parents:
                for child in parent.children.all():
                    if str(child.user.uid) != student.uid:
                        sibling_list.append(child)
            sibling = set(sibling_list)
            return sibling

    def get(self, request, student):
        try:
            cu = CustomUser.objects.get(uid=student)
            if cu.is_student():
                context = {}
                context["user"] = cu
                context["user_type"] = "student"
                context["siblings"] = self.get_siblings(cu)
                return render(request, self.template_name, context=context)
            else:
                raise Http404("Student Not Found")
        except Exception as e:
            raise Http404(f"Student Not Found: {e}")


class StudentLandingView(
    LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin, TemplateView
):
    permission_required = ["users.view_student"]
    template_name = "users/student_landing.html"

    def test_func(self):
        return self.request.user.is_student() or self.request.user.is_superuser

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


# Staff Section
class StaffIndexView(LoginRequiredMixin, View):
    template_name = "users/staff_landing.html"

    def get(self, request):
        if not request.user.is_school_staff() and not request.user.is_superuser:
            return redirect("school:home")
        else:
            return render(request, self.template_name)


class StaffProfileView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    template_name = "users/profile_beta.html"
    permission_required = ["users.view_staff"]
    model = Staff

    def get(self, request, staff):
        try:
            cu = CustomUser.objects.get(uid=staff)
            if cu.is_school_staff():
                context = {}
                context["user"] = cu
                context["user_type"] = "staff"
                return render(request, self.template_name, context=context)
            else:
                raise Http404("Staff Not Found")
        except Exception as e:
            raise Http404(f"Staff Not Found: {e}")


class StaffViewStudent(View):
    def get(self, request):
        return redirect("school:view_students", permanent=True)


class ViewStudents(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = [
        "users.view_student",
    ]
    template_name = "users/view_students.html"

    def generate_alphabet_index(self):
        """
        Iterate through student objects add increment letter dict using
        surname. After iteration, in template check if count/len>0 render in
        colour if exists, else disabled/greyed out if not. In the corresponding view,
        raise 404 is letter has no surnames that begin with that letter
        """
        import string

        letters = {letter: 0 for letter in string.ascii_lowercase}
        letters["."] = 0
        qs = Student.objects.all()
        for student in qs:
            letters[student.user.full_name(False, True)[0].lower()] += 1
        return letters

    def get_context_data(self):
        context = super().get_context_data()
        context["houses"] = Student.House
        context["years"] = Student.Year
        context["alpha"] = self.generate_alphabet_index()
        return context

    def post(self, request):
        search_string = request.POST["search-student-text"].strip()
        context = self.get_context_data()
        if len(search_string) >= 3:
            q1 = Q(user__first_name__icontains=search_string)
            q2 = Q(user__common_name__icontains=search_string)
            q3 = Q(user__last_name__icontains=search_string)
            students = Student.objects.filter(q1 | q2 | q3)
            context["query"] = search_string
            context["students"] = students
        else:
            context["query_error"] = True
        return render(request, self.template_name, context=context)


class ViewStudentAlpha(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = ["users.view_student", "users.view_staff"]
    template_name = "users/view_students_a_z.html"
    paginate_by = 10

    def get(self, request, letter):
        letter = letter.upper()
        qs = (
            Student.objects.filter(user__last_name__istartswith=letter)
            .all()
            .order_by(
                "year",
                "user__first_name",
            )
        )
        if not qs:
            raise Http404(f"No students with surnames that begin with {letter}")
        context = dict()
        context["qs"] = qs
        context["letter"] = letter
        return render(request, self.template_name, context=context)


class ViewStudentHouse(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = ["users.view_student", "users.view_staff"]
    template_name = "users/view_students_house.html"

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
            if qs.count() > 0:
                context = {}
                context["qs"] = qs
                context["house"] = house
                return render(request, self.template_name, context=context)
            else:
                raise Http404("House has no students.")

        else:
            raise Http404("House does not exist or is not accessible.")


class StaffViewStudentYear(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = ["users.view_student", "users.view_staff"]
    template_name = "users/view_students_year.html"

    def get(self, request, year):
        if year.lower() in [e.name.lower() for e in Student.Year]:
            output = [e.value for e in Student.Year if year.lower() == e.name.lower()]
            qs = (
                Student.objects.filter(year=output[0])
                .all()
                .order_by(
                    "house",
                    "user__first_name",
                )
            )
            if qs.count() > 0:
                context = {}
                context["qs"] = qs
                context["year"] = year
                return render(request, self.template_name, context=context)
            else:
                raise Http404("Year has no students.")
        else:
            raise Http404("Year does not exist or is not accessible.")


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


# SCHOOL CURRICULUA SECTION START
class CourseCategoryView(ListView):
    model = CourseCategory
    template_name = "school/course_category_list.html"


class CoursesView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = BasicCourse
    template_name = "school/course_list.html"

    def get(self, request, obj=None):
        return redirect("school:courses_view_all", permanent=True)

    # Use UserPassesTestMixin here rather than perm check
    # as Students also have that perm in their group
    def test_func(self):
        return self.request.user.is_school_staff() or self.request.user.is_superuser


class CourseView(DetailView):
    model = BasicCourse
    template_name = "school/course_detail.html"
    slug_url_kwarg = "slug"


class CourseViewStaff(View):
    def get(self, request, slug):
        return redirect("school:course_detail", slug=slug, permanent=True)


class CourseAdd(PermissionRequiredMixin, CreateView):
    permission_required = ["school.add_basiccourse"]
    model = BasicCourse
    fields = [
        "name",
        "course_code",
        "category",
        "course_type",
        "required",
        "description",
        "owner",
    ]
    template_name = "school/course_add.html"
    raise_exception = True
    success_message = "Course created successfully."

    def form_valid(self, form):
        try:
            if not form.instance.owner:
                form.instance.owner = self.request.user.staff
        except Exception:
            form.instance.owner = Staff.objects.filter(is_head_of_house=True).first()
        return super().form_valid(form)


class CourseEdit(
    LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin, UpdateView
):
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


class CourseDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = [
        "school.change_basiccourse",
        "school.change_basicclass",
    ]
    permission_denied_message = "Access Forbidden"
    model = BasicCourse
    template_name = "school/course_delete.html"
    success_url = reverse_lazy("school:courses_view_all")

    # def get(self, request, slug, obj=None):
    #     raise Exception(request.user.get_all_permissions())


class CourseOwnershipChangeView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ["school.change_basiccourse"]
    permission_denied_message = "Access Forbidden"
    model = BasicCourse
    success_url = reverse_lazy("school:courses_view_all")

    def get(self, request, *args, **kwargs):
        course = self.model.objects.get(slug=kwargs["slug"])
        if not course.owner:
            if (
                request.user.staff.staff_type == Staff.StaffType.ACADEMIC
                or request.user.staff.is_head_of_house
                or request.user.is_superuser
            ):
                course.owner = request.user.staff
                course.save()

        else:
            if course.owner == request.user.staff:
                course.owner = None
                course.save()
        return redirect("school:course_detail", kwargs["slug"])


# Class Section
class ClassesView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = BasicClass
    template_name = "school/class_list_all.html"

    def test_func(self):
        return self.request.user.is_school_staff() or self.request.user.is_superuser


class ClassView(PermissionRequiredMixin, DetailView):
    permission_required = ["school.view_basicclass"]
    model = BasicClass
    template_name = "school/class_detail.html"
    slug_url_kwarg = "class_slug"

    def get(self, request, *args, **kwargs):
        context = {}
        context["object"] = BasicClass.objects.get(slug=kwargs["class_slug"])
        obj = context["object"]

        if request.user.is_student():
            if obj not in request.user.student.basicclass_set.all():
                return redirect("school:course_detail", obj.course.slug, permanent=True)

        return render(request, template_name=self.template_name, context=context)


class ClassAdd(PermissionRequiredMixin, CreateView):
    permission_required = ["school.add_basicclass"]
    model = BasicClass
    form_class = ClassAddForm
    template_name = "school/class_add.html"
    raise_exception = True
    success_message = "Class created successfully."

    def get_context_data(self, **kwargs):
        context = super(ClassAdd, self).get_context_data(**kwargs)
        context["course"] = BasicCourse.objects.get(slug=self.kwargs["slug"])
        # context["slug"] = self.kwargs["slug"]
        return context

    def form_valid(self, form):
        form.instance.course = BasicCourse.objects.get(slug=self.kwargs["slug"])
        form.save()
        return super(ClassAdd, self).form_valid(form)


class ClassEdit(PermissionRequiredMixin, UserPassesTestMixin, UpdateView):
    permission_required = [
        "school.add_basicclass",
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
        if not school_class.course.owner:
            return True

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
@login_required
def home(request):
    if request.user.is_student():
        return redirect("school:student_main")
    elif request.user.is_school_staff():
        return redirect("school:staff_main")
    elif request.user.is_parent():
        return redirect("school:parent_main")
    else:
        return HttpResponse(f"{request.user} has a non-standard account")
