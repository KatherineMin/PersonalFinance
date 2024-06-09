import os
from dotenv import load_dotenv
import json
from retry import retry

from googleapiclient.discovery import build

from get_credentials import get_credential

import warnings ##
warnings.simplefilter(action='ignore', category=FutureWarning) ##


@retry(tries=3)
def access_sheet():
    creds = get_credential()
    load_dotenv()

    if os.getenv('SPREADSHEET_ID'):
        spreadsheet_id = os.getenv('SPREADSHEET_ID')
    else:
        spreadsheet_id = input("Enter spreadsheet's ID: ")

    try:
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()
        return sheet, spreadsheet_id

    except OSError:
        print("Google service has got disconnected. Trying to connect again.")
        return access_sheet()


def store_gs_meta():
    sheet, spreadsheet_id = access_sheet()
    meta = sheet.get(spreadsheetId=spreadsheet_id).execute()
    meta_data = {i: {'title': e['properties']['title'], 'sheetId': e['properties']['sheetId']} for i, e in enumerate(meta['sheets'])} ## Add column names as well

    with open("gs_meta_data.json", "w") as outfile:
        json.dump(meta_data, outfile)
