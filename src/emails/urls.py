from django.urls import path

from emails import views

# Patterns
#
urlpatterns = [
    path("google", views.connect_to_gmail, name="connect-google"),
    path("oauth", views.oauth2callback, name="connect-oauth"),
]
