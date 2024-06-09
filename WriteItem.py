import os
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
import re

from googleapiclient.errors import HttpError

from AccessSheet import access_sheet, store_gs_meta
from tools import get_sheet_id

load_dotenv()
MONTHLY_COLUMN_NAMES = os.getenv("MONTHLY_COLUMN_NAMES").split(', ')


def get_category(type: bool) -> str:
    if type:
        cat = os.getenv("SPENDING_CATEGORIES").split(", ")
    else:
        cat = os.getenv("EARNING_CATEGORIES").split(", ")

    print("Categories:")
    for i, e in enumerate(cat):
        print(f"{i}. {e}")

    while True:
        user_input = input("Choose a category by entering the number or typing the name")
        try:
            user_input = int(user_input)
            try:
                category = cat[user_input]
                return category
            except IndexError:
                print("Invalid choice, try again")

        except ValueError:
            category = str(user_input)
            if category in cat:
                return category
            else:
                print("Invalid choice, try again")


def get_currency(type: bool, currency_input: str) -> str:
    if type is True:
        if f"Spending ({currency_input})" in MONTHLY_COLUMN_NAMES:
            return currency_input
        else:
            retry_input = input(f"Cannot find the given currency code - {currency_input} (hint: Use ISO 4217 currency codes such as USD)")
            return get_currency(type, currency_input=retry_input)
    if type is False:
        if f"Earning ({currency_input})" in MONTHLY_COLUMN_NAMES:
            return currency_input
        else:
            retry_input = input(f"Cannot find the given currency code - {currency_input} (hint: Use ISO 4217 currency codes such as USD)")
            return get_currency(type, currency_input=retry_input)


def create_row_load(date: str, type:bool, currency: str, money_value: float, category: str, content:str=None) -> list:
    row_dict = {k: '' for k in MONTHLY_COLUMN_NAMES}
    row_dict['Date'] = date
    row_dict['Content'] = content
    row_dict['Category'] = category
    if type is True:
        row_dict[f"Spending ({currency})"] = money_value
    if type is False:
        row_dict[f"Earning ({currency})"] = money_value

    values = []
    for k, val in row_dict.items():
        if k == 'Date':
            values.append(
                [{
                    "userEnteredValue": {"stringValue": val},
                    "userEnteredFormat": {
                        "numberFormat": {
                            "type": "DATE",
                            "pattern": "YYYY-mm-dd"
                        }
                    }
                }]
            )
        elif k in ['Content', 'Category']:
            if val is None:
                val = ''
            values.append(
                [{"userEnteredValue": {"stringValue": val}}]
            )
        else:
            if val != '':
                values.append(
                    [{"userEnteredValue": {"numberValue": val}}]
                )
            else:
                values.append(
                    [{"userEnteredValue": {"stringValue": val}}]
                )
    return [{"values": values}]


def write_item(sheet_title: str):
    sheet, spreadsheet_id = access_sheet()
    sheet_id = get_sheet_id(sheet_title=sheet_title)
    while True:
        date = input("Enter date: ")
        try:
            date = pd.to_datetime(date)
            break
        except ValueError:
            print("Invalid value, try again (hint: 2024-04-01 ISO 8601 format)")

    content = str(input("Enter content: "))
    while True:
        type = str(input("Is it spend? Y/N"))
        if type.lower() in ['y', 'yes', 'true']:
            type = True
            break
        elif type.lower() in ['n', 'no', 'false']:
            type = False
            break
        else:
            print("Invalid value, try again (hint: answer it Yes or No)")

    amount = input("Enter amount with currency code (eg. USD 1000.99)")
    currency = ''.join(re.split("[^a-zA-Z]*", amount)).upper().strip()
    value = ''.join(re.split("[^0-9,.]*", amount))

    currency = get_currency(type, currency)
    while True:
        try:
            value = float(value)
            break
        except ValueError:
            value = input("Invalid dollar value, provide valid amount (hint: 4000.19)")

    category = get_category(type)

    rows = create_row_load(date=datetime.strftime(date, '%Y-%m-%d'),
                           type=type,
                           currency=currency,
                           money_value=value,
                           category=category,
                           content=content
                           )
    body = {
        "appendCells": {
            "sheetId": sheet_id,
            "rows": rows,
            "fields": "*"
        }
    }

    try:
        sheet.batchUpdate(spreadsheetId=spreadsheet_id, body={"requests": [body]}).execute()
    except HttpError as e:
        print(f"Caught an HttpError: {e}")
        raise e
