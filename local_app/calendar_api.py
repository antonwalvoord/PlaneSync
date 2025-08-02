import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

calendarId = "c_995ce50a3385438bcc66d34fd4d5faf5ff95339d49d31d40b0de514ba839d822@group.calendar.google.com"
tokenPath = "/home/aewal/NFR26/timeline_tools/local_app/token.json"
credPath = "/home/aewal/NFR26/timeline_tools/local_app/credentials.json"

creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists(tokenPath):
    creds = Credentials.from_authorized_user_file(tokenPath, SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            credPath, SCOPES
        )
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open(tokenPath, "w") as token:
        token.write(creds.to_json())

try:
    service = build("calendar", "v3", credentials=creds)

except HttpError as error:
    print(f"An error occurred: {error}")


def get_event(eventId):
    try:
        event = service.events().get(
            calendarId=calendarId,
            eventId=eventId,
        ).execute()
    except Exception:
        return Exception
    else:
        print("Found an existing event")
        return event
