from django import forms
from django.contrib.auth.forms import AuthenticationForm, UsernameField


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        self.error_messages[
            "invalid_login"
        ] = "Please check your username and password and try again."
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = UsernameField(
        label="Username",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "",
                "id": "username",
            }
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "",
                "id": "password",
            }
        )
    )
