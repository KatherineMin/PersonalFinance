import os.path
import sys

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from oauth2client.service_account import ServiceAccountCredentials

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_KEY_FILE = 'client_secret.json'


def get_credential():
  """Creates a Credential object with the correct OAuth2 authorization.

  Uses the service account key stored in SERVICE_ACCOUNT_KEY_FILE.

  Returns:
    Credentials, the user's credential.
  """
  credential = ServiceAccountCredentials.from_json_keyfile_name(
    SERVICE_ACCOUNT_KEY_FILE, SCOPES)

  if not credential or credential.invalid:
    print('Unable to authenticate using service account key.')
    sys.exit()
  return credential


def rewrite_token():
  flow = InstalledAppFlow.from_client_secrets_file(
    "credentials.json", SCOPES
  )
  creds = flow.run_local_server(port=0)
  with open("token.json", "w") as token:
    token.write(creds.to_json())


def return_credentials():
  """Returns valid credentials, refreshing them if necessary."""
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      try:
        creds.refresh(Request())
      except RefreshError:
        rewrite_token()
        # print("Token refresh failed. Please re-authenticate.")
        # return None
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
        "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  return creds

