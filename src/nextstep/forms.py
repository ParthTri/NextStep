from django import forms

from nextstep import models


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = models.Application
        fields = ["role", "company", "applied_timestamp"]

        widgets = {
            "role": forms.TextInput(attrs={"class": "brutal-input"}),
            "company": forms.TextInput(attrs={"class": "brutal-input"}),
            "applied_timestamp": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "datetime-neo"}
            ),
        }
