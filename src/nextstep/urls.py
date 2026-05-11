from django.urls import path

from nextstep import views

# Patterns
#
urlpatterns = [
    path("", views.Dashboard.as_view(), name="dashboard"),
    path("stats", views.Stats, name="stats"),
    path("application/<int:pk>", views.ApplicationView.as_view(), name="application"),
    path(
        "application/<int:pk>/update",
        views.ApplicationUpdateView.as_view(),
        name="application-update",
    ),
    path(
        "application/<int:pk>/delete",
        views.ApplicationDelete,
        name="application-delete",
    ),
    path("settings", views.Settings.as_view(), name="settings"),
    path("tag/<int:tag_id>/delete", views.TagRemove, name="tag-remove"),
    path("signin", views.LoginView.as_view(), name="signin"),
    path("signup", views.SignupView.as_view(), name="signup"),
    path("logout", views.logout_handler, name="logout"),
]
