from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.utils import timesince
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

    def post(self, request: HttpRequest, *args, **kwargs):

        application_form = forms.ApplicationForm(request.POST)

        if application_form.is_valid():
            application = application_form.save()
            tag = models.Tag.objects.get(name="Applied")
            application.tags.add(tag)
            application.save()

            return redirect("dashboard")


class ApplicationView(View):
    template_name = "application.html"

    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}

        application = models.Application.objects.get(id=kwargs.get("pk"))

        context["application"] = application
        context["tags"] = application.tags.all()
        context["current_tag"] = application.get_current_tag()
        context["elapsed_days"] = timesince.timesince(application.applied_timestamp)

        return render(request, self.template_name, context)

