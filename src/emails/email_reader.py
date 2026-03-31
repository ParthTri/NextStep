import base64
import time
from typing import List

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from nextstep import models


def get_creds_and_build(account: models.UserEmailAccount):
    # 1. Fetch the active Gmail account for this user
    if not account or account.provider != "GMAIL":
        raise Exception("Error: No active Gmail account connected for this user.")

    # 2. Get the credentials object (handles encryption & refreshing internally)
    try:
        creds = account.get_google_creds()
    except Exception as e:
        return f"Error refreshing credentials: {str(e)}"

    # 3. Build the service
    service = build("gmail", "v1", credentials=creds)
    return service


def get_email_body(payload):
    """
    Recursively searches for the 'data' key in a Gmail message payload.
    """
    # 1. Check if the data is in the top-level body (rare for modern emails)
    body_data = payload.get("body", {}).get("data")
    if body_data:
        return decode_base64(body_data)

    # 2. If not, look through 'parts'
    parts = payload.get("parts", [])
    for part in parts:
        # Check this part's body
        part_data = part.get("body", {}).get("data")
        if part_data:
            return decode_base64(part_data)

        # If this part has its own nested parts, recurse!
        if "parts" in part:
            return get_email_body(part)

    return ""


def decode_base64(data):
    # Gmail uses URL-safe base64
    decoded = base64.urlsafe_b64decode(data)
    return decoded.decode("utf-8", errors="replace")


def get_latest_emails(service) -> List[dict[str, str]] | str:
    # 1. Search for emails in the last 30 mins
    thirty_mins_ago = int(time.time() - (30 * 60))
    query = f"in:inbox after:{thirty_mins_ago}"

    results = service.users().messages().list(userId="me", q=query).execute()
    messages = results.get("messages", [])

    return messages


def read_emails(service, messages) -> List[str]:
    message_content = []

    for message in messages:
        if type(message) is dict:
            message_data = (
                service.users()
                .messages()
                .get(userId="me", id=message.get("id"))
                .execute()
            )
            body = get_email_body(message_data.get("payload"))
            message_content.append(body)

    return message_content
