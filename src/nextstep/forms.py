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


class ApplicationUpdateForm(forms.ModelForm):
    tags = forms.ModelChoiceField(
        queryset=models.Tag.objects.all(),
        widget=forms.Select(attrs={"class": "select-neo h-10"}),
    )

    class Meta:
        model = models.Application
        fields = [
            "role",
            "role_link",
            "company",
            "company_link",
            "job_description",
        ]

        widgets = {
            "role": forms.TextInput(attrs={"class": "brutal-input w-full"}),
            "role_link": forms.TextInput(attrs={"class": "brutal-input w-full"}),
            "company": forms.TextInput(attrs={"class": "brutal-input"}),
            "company_link": forms.TextInput(attrs={"class": "brutal-input"}),
            "job_description": forms.Textarea(attrs={"class": "area-neo"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields.get("tags").initial = self.instance.get_current_tag()

    def save(self, commit: bool = True):
        self.instance.role = self.cleaned_data.get("role")
        self.instance.role_link = self.cleaned_data.get("role_link")
        self.instance.company = self.cleaned_data.get("company")
        self.instance.company_link = self.cleaned_data.get("company_link")
        self.instance.job_description = self.cleaned_data.get("job_description")

        if commit:
            if self.fields.get("tags").initial != self.cleaned_data.get("tags"):
                tag = models.ApplicationTag.objects.create(
                    application=self.instance, tag=self.cleaned_data.get("tags")
                )
            self.instance.save()

        return self.instance
