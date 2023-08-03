from django import forms
from .models import BasicCourse, BasicClass, SchoolYear
from users.models import Staff, Student
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
        widget=widgets.SelectMultiple(
            attrs={
                "size": "15",
            }
        ),
    )

    # widgets = {"teacher": widgets.CheckboxSelectMultiple}


class ClassUpdateForm(forms.ModelForm):
    slug = forms.CharField(disabled=True)

    class Meta:
        model = BasicClass
        fields = [
            "name",
            "course",
            "school_year",
            "teacher",
            "slug",
        ]

    teacher = forms.ModelMultipleChoiceField(
        queryset=Staff.objects.filter(staff_type="AC").all(),
        widget=widgets.SelectMultiple(
            attrs={
                "size": "15",
            }
        ),
    )


class ClassEnrolForm(forms.ModelForm):
    class Meta:
        model = BasicClass
        fields = ["student"]

    student = forms.ModelMultipleChoiceField(
        required=True,
        label="Enroled Student(s)",
        queryset=Student.objects.all().order_by("house", "year", "user__last_name"),
        widget=widgets.CheckboxSelectMultiple(
            attrs={
                "size": "15",
            }
        ),
    )


class ScheduleAddForm(forms.ModelForm):
    start_date = forms.DateField(
        widget=widgets.DateInput(
            format="%Y-%m-%d",
            attrs={
                "class": "form-control",
                "type": "date",
            },
        )
    )
    end_date = forms.DateField(
        widget=widgets.DateInput(
            format="%Y-%m-%d",
            attrs={
                "class": "form-control",
                "type": "date",
            },
        )
    )

    class Meta:
        model = SchoolYear
        fields = "__all__"


class ScheduleUpdateForm(forms.ModelForm):
    slug = forms.CharField(disabled=True)
    start_date = forms.DateField(
        widget=widgets.DateInput(
            format="%Y-%m-%d",
            attrs={
                "class": "form-control",
                "type": "date",
            },
        )
    )
    end_date = forms.DateField(
        widget=widgets.DateInput(
            format="%Y-%m-%d",
            attrs={
                "class": "form-control",
                "type": "date",
            },
        )
    )

    class Meta:
        model = SchoolYear
        fields = "__all__"
