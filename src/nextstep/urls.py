from django.urls import path

from nextstep import views

# Patterns
#
urlpatterns = [path("", views.dashboard, name="dashboard")]
