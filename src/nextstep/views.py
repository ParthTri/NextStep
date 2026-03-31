import logging

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.utils import timesince
from django.views import View

from nextstep import forms, models

# Create your views here.


# TODO: Create initial view to signup and create a user
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
