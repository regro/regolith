from __future__ import print_function
import datetime
import os
import pathlib
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


def add_to_google_calendar(event):
    """Takes a newly created event, and adds it to the user's google calendar

    Parameters:
        event - a dictionary containing the event details to be added to google calendar
                https://developers.google.com/calendar/api/v3/reference/events

    Returns:
        None
    """

    SCOPES = ['https://www.googleapis.com/auth/calendar.events']
    tokendir = pathlib.Path('tokens', 'google_calendar')
    creds = None
    os.makedirs(tokendir, exist_ok=True)
    tokenfile = os.path.join(tokendir, 'token.json')
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(tokenfile):
        creds = Credentials.from_authorized_user_file(tokenfile, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            curr = pathlib.Path(__file__).parent.resolve()
            print(curr)
            flow = InstalledAppFlow.from_client_secrets_file(
                os.path.join(curr, 'credentials.json'),
                SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(tokenfile, 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))

