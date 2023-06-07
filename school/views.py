from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse, HttpResponseForbidden
from django.views.generic import ListView, DetailView
from users.models import Parent, CustomUser, Student


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


@login_required
def parent(request):
    if not request.user.is_parent() and not request.user.is_superuser:
        return redirect("school:home")
    else:
        return HttpResponse(f"Welcome Parent {request.user}")


class ParentChild(PermissionRequiredMixin, ListView):
    model = Parent
    permission_required = [
        "users.view_parent",
    ]

    def get_queryset(self):
        return Parent.objects.filter(user=self.request.user)


class Child(PermissionRequiredMixin, DetailView):
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
