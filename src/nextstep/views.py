from django.http import HttpRequest
from django.shortcuts import render

from nextstep import forms, models


# Create your views here.
def dashboard(request: HttpRequest):
    context = {}

    application_form = forms.ApplicationForm()

    context["application_form"] = application_form

    return render(request, "dashboard.html", context)
