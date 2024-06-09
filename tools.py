import re
import requests
from retry import retry
import json


def remove_currency_symbol(string):
    try:
        conv_val = float(re.sub(r'[^\d.]', '', string))
    except ValueError:
        conv_val = None
    return conv_val


@retry(tries=3)
def get_currency_rate(base_currency):
    response = requests.get(f"https://open.er-api.com/v6/latest/{base_currency}")
    res_json = response.json()

    with open("currency_rate.json", "w") as outfile:
        json.dump(res_json, outfile)


def relabel_month_year_ko(month_year):
    month, year = month_year.lower().split(' ')
    month_dict = {'jan': "1월", 'feb': "2월", 'mar': "3월", 'apr': "4월", 'may': "5월", 'jun': "6월",
                  'jul': "7월",'aug': "8월", 'sep': "9월", 'oct': "10월", 'nov': "11월", 'dec': "12월"}
    for k, m in month_dict.items():
        if month == k:
            re_month = m
    re_year = '20' + year

    return re_month, re_year


def relabel_month_year(month_year):
    month, year = month_year.lower().split(' ')
    month_dict = {'jan': "January", 'feb': "February", 'mar': "March", 'apr': "April", 'may': "May", 'jun': "June",
                  'jul': "July", 'aug': "August", 'sep': "September", 'oct': "October", 'nov': "November", 'dec': "December"}
    for k, m in month_dict.items():
        if month == k:
            re_month = m
    re_year = '20' + year

    return re_month, re_year


def get_sheet_id(sheet_title: str) -> int:
    with open("gs_meta_data.json", "r") as f:
        meta_data = json.loads(f.read())
        f.close()

    sheet_id = None  # Initialize sheet_id

    for k, val in meta_data.items():
        if val['title'] == sheet_title:
            sheet_id = val['sheetId']
            break  # Exit the loop once the sheet_id is found

    if sheet_id is not None:
        return sheet_id
    else:
        raise ValueError(f"{sheet_title} doesn't exist")

