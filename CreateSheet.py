import os
from dotenv import load_dotenv
from googleapiclient.errors import HttpError

from AccessSheet import access_sheet, store_gs_meta


def create_monthly_sheet(sheet_title: str):
    load_dotenv()
    columns = os.getenv("MONTHLY_COLUMN_NAMES")
    sheet, spreadsheet_id = access_sheet()
    sheet.create()
    body = {
        "requests": {
            "addSheet": {
                "properties": {
                    "title": sheet_title,
                    "index": 1
                }
            }
        }
    }

    res = sheet.batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
    store_gs_meta()

    sheet_id = res['replies'][0]['addSheet']['properties']['sheetId']

    body = {
        "updateCells": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": 0,
                "endRowIndex": 1,
                "startColumnIndex": 0,
                "endColumnIndex": len(columns.split(', '))
            },
            "rows": [
                {
                    "values": [
                        {"userEnteredValue": {"stringValue": c}} for c in columns.split(', ')
                    ]  # Modify the structure to include "userEnteredValue"
                }
            ],
            "fields": "*"
        }
    }


    try:
        sheet.batchUpdate(spreadsheetId=spreadsheet_id, body={"requests": [body]}).execute()
        print(f"New sheet {sheet_title} is created!")
    except HttpError as e:
        print(f"Caught an HttpError: {e}")
        raise e
