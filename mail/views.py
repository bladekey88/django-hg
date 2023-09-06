from django.views import View
from django.http import HttpResponse
from django.core.mail import send_mass_mail
from users.models import Staff, Student
from userprofile.settings import EMAIL_HOST_USERNAME, EMAIL_HOST_PASSWORD
from smtplib import SMTPDataError
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)


class MainView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return any([self.request.user.is_superuser, self.request.user.is_staff])

    def get(self, request):
        subject = "Test Email"
        message: str = (
            """This is a test mail. You do not need to take any further actions."""
        )
        from_email = EMAIL_HOST_USERNAME
        recipient_list = [request]
        messages = [
            (subject, message, from_email, [r.user.email]) for r in recipient_list
        ]
        try:
            send_mass_mail(
                messages,
                fail_silently=False,
                auth_user=EMAIL_HOST_USERNAME,
                auth_password=EMAIL_HOST_PASSWORD,
            )
            return HttpResponse("Sent Email")
        except SMTPDataError as e:
            raise PermissionDenied("Access Denied -", e)
