from django import forms
from .models import BasicCourse, BasicClass
from users.models import Staff
from django.forms import widgets


class CourseUpdateForm(forms.ModelForm):
    slug = forms.CharField(disabled=True)
    course_code = forms.CharField(disabled=True)

    class Meta:
        model = BasicCourse
        fields = "__all__"


class ClassAddForm(forms.ModelForm):
    class Meta:
        model = BasicClass
        fields = [
            "name",
            "school_year",
            "teacher",
        ]

    teacher = forms.ModelMultipleChoiceField(
        queryset=Staff.objects.filter(staff_type="AC").all(),
        widget=widgets.SelectMultiple,
    )

    widgets = {"teacher": widgets.CheckboxSelectMultiple}
