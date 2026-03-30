import os

from django.conf import settings
from django.shortcuts import redirect
from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from nextstep import models

load_dotenv()

# This scope allows reading but not deleting/sending
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

if settings.DEBUG:
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


def connect_to_gmail(request):
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
        # Ensure this matches your Redirect URI in Google Console exactly
        redirect_uri=request.build_absolute_uri("/connect/oauth"),
    )

    # prompt='consent' and access_type='offline' are REQUIRED to get a refresh_token
    authorization_url, state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true", prompt="consent"
    )

    # Store the state so the callback can verify it
    request.session["oauth_state"] = state
    request.session["code_verifier"] = flow.code_verifier
    return redirect(authorization_url)


def oauth2callback(request):
    state = request.session.get("oauth_state")
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
        state=state,
        redirect_uri=request.build_absolute_uri("/connect/oauth"),
    )
    flow.code_verifier = request.session.get("code_verifier")

    # Fetch the token using the URL Google sent the user back to
    authorization_response = request.build_absolute_uri()

    flow.fetch_token(authorization_response=authorization_response)
    creds = flow.credentials

    # Get the user's email address using the Gmail API
    service = build("gmail", "v1", credentials=creds)
    profile = service.users().getProfile(userId="me").execute()
    email_address = profile.get("emailAddress")

    # Save to your Model
    account, created = models.UserEmailAccount.objects.update_or_create(
        user=request.user,
        defaults={
            "provider": "GMAIL",
            "email_address": email_address,
            "access_token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_expiry": creds.expiry,
            "is_active": True,
        },
    )

    return redirect("dashboard")
