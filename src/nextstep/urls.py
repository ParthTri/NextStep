from django.urls import path

from nextstep import views

# Patterns
#
urlpatterns = [
    path("", views.Dashboard.as_view(), name="dashboard"),
    path("application/<int:pk>", views.ApplicationView.as_view(), name="application"),
]
