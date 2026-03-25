from django.http import HttpRequest
from django.shortcuts import render
from django.views import View

from nextstep import forms, models


# Create your views here.
class Dashboard(View):
    template_name = "dashboard.html"

    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}

        applications = (
            models.Application.objects.all()
            .order_by("-applied_timestamp", "role")
            .prefetch_related("tags")
        )
        application_form = forms.ApplicationForm()

        context["applications"] = applications
        context["application_form"] = application_form

        return render(request, self.template_name, context)
