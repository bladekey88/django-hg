from django import forms
from .models import BorrowerFine


class BorrowerFineAddForm(forms.ModelForm):
    class Meta:
        model = BorrowerFine
        fields = ["borrower", "item", "fine"]
        exclude = ["status"]
