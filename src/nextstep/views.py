import json
import logging
from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import Http404, HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timesince
from django.views import View

from nextstep import forms, models
from nextstep.utils import colours


# Create your views here.
class LoginView(View):
    template_name = "auth/signin.html"

    def get(self, request, *args, **kwargs):
        context = {}

        signin_form = forms.SigninForm()
        context["signin_form"] = signin_form
        context["user"] = False

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {}
        signin_form = forms.SigninForm(request.POST)
        context["signin_form"] = signin_form
        context["user"] = False

        if signin_form.is_valid():
            user = authenticate(
                username=signin_form.cleaned_data.get("username"),
                password=signin_form.cleaned_data.get("password"),
            )
            if user is not None:
                login(request, user)
                return redirect("dashboard")
            else:
                context["form_error"] = "Username or password is not correct."
                return render(request, self.template_name, context)
        else:
            return render(request, self.template_name, context)


class SignupView(View):
    template_name = "auth/signup.html"

    def get(self, request, *args, **kwargs):
        context = {}

        signup_form = forms.SignupForm()
        context["signup_form"] = signup_form
        context["user"] = False

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {}
        signup_form = forms.SignupForm(request.POST)
        context["signup_form"] = signup_form
        context["user"] = False

        if signup_form.is_valid():
            try:
                user = User.objects.create_user(
                    username=signup_form.cleaned_data.get("username"),
                    email=signup_form.cleaned_data.get("email"),
                    password=signup_form.cleaned_data.get("password"),
                )
            except Exception as e:
                context["form_error"] = (
                    "Oops something went wrong, please try again later"
                )
                logger = logging.getLogger()
                logger.error(f"Could not signup user, got '{e}'")

                return render(request, self.template_name, context)
            else:
                login(request, user)
                return redirect("dashboard")
        else:
            return render(request, self.template_name, context)


def logout_handler(request):
    """Logging out users"""

    logout(request)

    return redirect("signin")


class Dashboard(LoginRequiredMixin, View):
    template_name = "dashboard.html"
    login_url = "/signin"

    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}

        applications = (
            models.Application.objects.filter(user=request.user)
            .order_by("-applied_timestamp", "role")
            .prefetch_related("tags")
        )
        application_form = forms.ApplicationForm()

        context["applications"] = applications
        context["application_form"] = application_form
        context["user"] = request.user

        return render(request, self.template_name, context)

    def post(self, request: HttpRequest, *args, **kwargs):

        application_form = forms.ApplicationForm(request.POST)

        if application_form.is_valid():
            application = application_form.save(user=request.user)
            tag = models.Tag.objects.get(name="Applied")
            application.tags.add(tag)
            application.save()

            return redirect("dashboard")


class ApplicationView(LoginRequiredMixin, View):
    template_name = "application.html"
    login_url = "/signin"

    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}

        application = models.Application.objects.get(id=kwargs.get("pk"))

        context["application"] = application
        context["tags"] = application.tags.all()

        context["application_tags"] = application.get_all_tags().order_by("updated_at")
        context["current_tag"] = application.get_current_tag()
        context["elapsed_days"] = timesince.timesince(application.applied_timestamp)

        return render(request, self.template_name, context)


class ApplicationUpdateView(LoginRequiredMixin, View):
    model = models.Application
    template_name = "application_update.html"

    def get(self, request, *args, **kwargs):
        context = {}

        application = models.Application.objects.get(id=kwargs.get("pk"))
        form = forms.ApplicationUpdateForm(instance=application)

        context["application"] = application
        context["form"] = form
        context["user"] = request.user

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        instance = models.Application.objects.get(id=kwargs.get("pk"))

        form = forms.ApplicationUpdateForm(request.POST, instance=instance)

        if form.is_valid():
            form.save()

            return redirect("application", pk=instance.id)
        else:
            return render(
                request, self.template_name, {"application": instance, "form": form}
            )


@login_required(login_url="/signin")
def ApplicationDelete(request, pk):
    application = get_object_or_404(models.Application, id=pk, user=request.user)

    application.delete()

    return redirect("dashboard")


@login_required(login_url="/signin")
def TagRemove(request, tag_id: int):
    if request.method == "POST":
        application_tag = get_object_or_404(models.ApplicationTag, id=tag_id)

        application_tag.delete()

        return redirect("application", pk=application_tag.application.id)
    else:
        raise Http404()


class Settings(LoginRequiredMixin, View):
    template_name = "settings.html"
    login_url = "/signin"

    def get(self, request, *args, **kwargs):
        context = {}

        tags = models.Tag.objects.filter(user=None)
        user_tags = models.Tag.objects.filter(user=request.user)

        context["tags"] = tags
        context["user_tags"] = user_tags
        context["user"] = request.user

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {}
        final_tags = request.POST.get("final_tags").split(",")

        for tag in final_tags:
            name, colour = tag.split("|")
            colour = colour[1::]

            models.Tag.objects.create(name=name, colour=colour, user=request.user)

        tags = models.Tag.objects.filter(user=None)
        user_tags = models.Tag.objects.filter(user=request.user)

        context["tags"] = tags
        context["user_tags"] = user_tags
        context["user"] = request.user

        return render(request, self.template_name, context)


@login_required(login_url="/signin")
def Stats(request):
    # Pie chart of applications
    applications = models.Application.objects.filter(
        user=request.user
    ).prefetch_related("tags")
    density = {}
    for application in applications:
        current_tag = application.get_current_tag()
        if application.get_current_tag() is None:
            continue

        count = density.get(current_tag, 0)
        if count == 0:
            density[current_tag] = 1
        else:
            density[current_tag] += 1

    # Bar chart for applications per month
    month_count = {}
    for application in applications:
        date: datetime = application.applied_timestamp
        if month_count.get(date.strftime("%B"), 0) == 0:
            month_count[date.strftime("%B")] = 1
        else:
            month_count[date.strftime("%B")] += 1

    bar_colours = [colours.generate_dynamic_neobrutal() for i in month_count.values()]

    flows = {}
    tag_colors = {tag.name: f"#{tag.colour}" for tag in models.Tag.objects.all()}
    for app in applications:
        # Get chronological sequence of tags
        history = list(
            app.get_all_tags()
            .order_by("updated_at")
            .values_list("tag__name", flat=True)
        )

        for i in range(len(history) - 1):
            source = history[i]
            target = history[i + 1]
            key = (source, target)
            flows[key] = flows.get(key, 0) + 1

    # Format for Chart.js Sankey
    sankey_data = [{"from": k[0], "to": k[1], "flow": v} for k, v in flows.items()]

    context = {
        "applications": applications,
        "doughnut_labels": list(map(lambda x: x.name, density.keys())),
        "doughnut_data": list(density.values()),
        "doughnut_colours": list(map(lambda x: f"#{x.colour}", density.keys())),
        "bar_labels": list(month_count.keys()),
        "bar_data": list(month_count.values()),
        "bar_colours": list(map(lambda x: colours.format_channels(x), bar_colours)),
        "bar_borders": list(
            map(
                lambda x: colours.format_channels(colours.darker_variant(x)),
                bar_colours,
            )
        ),
        "sankey_data_json": json.dumps(sankey_data),
        "tag_colors_json": json.dumps(tag_colors),
    }

    return render(request, "stats.html", context)
