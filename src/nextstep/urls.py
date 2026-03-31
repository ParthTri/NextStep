from django.urls import path

from nextstep import views

# Patterns
#
urlpatterns = [
    path("", views.Dashboard.as_view(), name="dashboard"),
    path("application/<int:pk>", views.ApplicationView.as_view(), name="application"),
    path(
        "application/<int:pk>/update",
        views.ApplicationUpdateView.as_view(),
        name="application-update",
    ),
    path("settings", views.Settings.as_view(), name="settings"),
    path("signin", views.LoginView.as_view(), name="signin"),
]
