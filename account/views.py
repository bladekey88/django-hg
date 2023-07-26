from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from users.models import CustomUser
from django_auth_ldap.backend import LDAPBackend
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from users.forms import CustomUserCreationForm

# Create your views here.


def dashboard(request):
    return render(request, "account/dashboard.html")


@login_required
def profile(request):
    try:
        ldap_data = LDAPBackend().populate_user(username=request.user.uid)
        ldap_info = ldap_data.ldap_user.attrs
        dn = ldap_data.ldap_user.dn

        try:
            manager_uid = ldap_info.get("manager")[0].split(",")[0][4:]
            manager = LDAPBackend().populate_user(username=manager_uid)
            manager_details = manager.ldap_user.attrs
        except Exception:
            manager_details = None

    except Exception:
        ldap_info = None
        dn = "Unable to retrieve from directory server"
        manager_details = None

    return render(
        request,
        "account/profile.html",
        {
            "user": request.user,
            "ldap_info": ldap_info,
            "ldap_dn": dn,
            "manager": manager_details,
        },
    )


@login_required
def profile_other_user(request, uid):
    get_user = get_object_or_404(CustomUser, uid=uid)
    try:
        ldap_data = LDAPBackend().populate_user(username=get_user.uid)
        ldap_info = ldap_data.ldap_user.attrs
        dn = ldap_data.ldap_user.dn
        try:
            manager_uid = ldap_info.get("manager")[0].split(",")[0][4:]
            manager = LDAPBackend().populate_user(username=manager_uid)
            manager_details = manager.ldap_user.attrs
        except Exception:
            manager_details = None

    except Exception:
        ldap_info = None
        dn = "Unable to retrieve from directory server"
        manager_details = None

    return render(
        request,
        "account/profile.html",
        {
            "user": get_user,
            "ldap_info": ldap_info,
            "ldap_dn": dn,
            "manager": manager_details,
        },
    )


class UserCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = ["users.add_customuser"]
    template_name = "account/create-user.html"
    model = CustomUser
    raise_exception = True
    # fields = "__all__"
    form_class = CustomUserCreationForm
