from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from account.forms import UserLoginForm

app_name = "account"

urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="account/login.html",
            authentication_form=UserLoginForm,
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
    path(
        "profile/<str:uid>/",
        views.profile_other_user,
        name="profile_other_user",
    ),
    path(
        "create-user/",
        views.UserCreateView.as_view(),
        name="create-user",
    ),
]
