import os
from dotenv import load_dotenv
import json
from datetime import datetime
import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt

from AccessSheet import access_sheet
from tools import remove_currency_symbol, get_currency_rate, relabel_month_year

pd.set_option('display.max_columns', 100)
today = datetime.today()


def spending_category_barplots(month_label: str, data: pd.DataFrame=None, purpose: str=None):
    if data.empty:
        print("Issue in data preparation")
    else:
        sns.set_style("darkgrid")
        sns.set_color_codes("bright")
        crayon_colors = sns.crayons

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(y='Category', x='Spending (CAD)', data=data, label='Spending (CAD)',
                    color=crayon_colors['Pine Green'], ax=ax)
        for i in range(len(data)):
            ax.barh(data['Category'][i], data['Spending (Conv)'][i], left=data['Spending (CAD)'][i],
                    color=crayon_colors['Yellow Green'], alpha=0.7, label='Spending (other currencies)' if i == 0 else "")

        max_val = max(data['Spending (CAD)'] + data['Spending (Conv)'])
        ax.set_xlim(0, max_val + 100)
        ax.legend(ncol=2, loc="lower right", frameon=True)
        fig.set_tight_layout({"pad": 1})
        month, year = relabel_month_year(month_label)

        if not purpose:
            purpose = 'personal'

        if purpose == 'personal':
            ax.set(ylabel="",
                   xlabel="\nTotal Spending in CAD",
                   title=f"Spending in {month + ' ' + year}\n")
            plt.savefig(f'plots/{month_label.lower().replace(" ", "_")}_spending_by_cat_personal.png', dpi=300)
            print(f"Monthly Spending chart for {month + ' ' + year} is created.")

        if purpose == 'sharing':
            ax.set(ylabel="",
                   xlabel="\nTotal Spending in CAD",
                   title=f"Spending in {month + ' ' + year}\n",
                   xticklabels=[])
            plt.savefig(f'plots/{month_label.lower().replace(" ", "_")}_spending_by_cat_sharing.png', dpi=300)
            print(f"Monthly Spending chart for {month + ' ' + year} is created.")


def earning_category_barplots(month_label: str, data: pd.DataFrame=None, purpose: str=None):
    if data.empty:
        print("Issue in data preparation")
    else:
        sns.set_style("darkgrid")
        sns.set_color_codes("bright")
        crayon_colors = sns.crayons

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(y='Category', x='Earning (CAD)', data=data, label='Earnings (CAD)',
                    color=crayon_colors['Red Violet'], ax=ax)
        for i in range(len(data)):
            ax.barh(data['Category'][i], data['Earning (Conv)'][i], left=data['Earning (CAD)'][i],
                    color=crayon_colors['Dandelion'], alpha=0.7, label='Earnings (other currencies)' if i == 0 else "")

        max_val = max(data['Earning (CAD)'] + data['Earning (Conv)'])
        ax.set_xlim(0, max_val + 100)
        ax.legend(ncol=2, loc="lower right", frameon=True)
        fig.set_tight_layout({"pad": 1})
        month, year = relabel_month_year(month_label)

        if not purpose:
            purpose = 'personal'

        if purpose == 'personal':
            ax.set(ylabel="",
                   xlabel="\nTotal Earnings in CAD",
                   title=f"Earning in {month + ' ' + year}\n")
            plt.savefig(f'plots/{month_label.lower().replace(" ", "_")}_earnings_by_cat_personal.png', dpi=300)
            print(f"Monthly Earnings chart for {month + ' ' + year} is created.")

        if purpose == 'sharing':
            ax.set(ylabel="",
                   xlabel="\nTotal Earnings in CAD",
                   title=f"Earnings in {month + ' ' + year}\n",
                   xticklabels=[])
            plt.savefig(f'plots/{month_label.lower().replace(" ", "_")}_earning_by_cat_sharing.png', dpi=300)
            print(f"Monthly Earnings chart for {month + ' ' + year} is created.")


def make_monthly_report(sheet_title=None):
    if sheet_title:
        sheet_title = sheet_title
    else:
        with open("gs_meta_data.json", "r") as f:
            meta_data = json.loads(f.read())
            f.close()
        sheet_title = meta_data['1']['title']

    sheet, spreadsheet_id = access_sheet()
    print(f"Start creating monthly reports for {sheet_title}")
    spreadsheet = sheet.values().get(spreadsheetId=spreadsheet_id, range=sheet_title).execute()
    load_dotenv()
    col_names = os.getenv('MONTHLY_COLUMN_NAMES').split(', ')
    spending_cols = [col for col in col_names if 'spend' in col.lower()]
    earning_cols = [col for col in col_names if 'earn' in col.lower()]
    spending_cats = os.getenv('SPENDING_CATEGORIES').split(', ')
    earning_cats = os.getenv('EARNING_CATEGORIES').split(', ')

    if len(spreadsheet['values'][0]) == len(col_names):
        spreadsheet_df = pd.DataFrame(spreadsheet['values'][1:]).iloc[:, :len(col_names)]
        spreadsheet_df.columns = col_names
        spreadsheet_df['Date'] = pd.to_datetime(spreadsheet_df['Date'])
        spreadsheet_df['Category'] = spreadsheet_df['Category'].apply(lambda x: x.strip())

        spreadsheet_df[spending_cols] = spreadsheet_df[spending_cols].applymap(lambda x: remove_currency_symbol(x))
        spreadsheet_df[earning_cols] = spreadsheet_df[earning_cols].applymap(lambda x: remove_currency_symbol(x))

        get_currency_rate('CAD')
        with open("currency_rate.json", "r") as f:
            currency_rate = json.loads(f.read())
            f.close()
        usd_rate = currency_rate['rates']['USD']
        krw_rate = currency_rate['rates']['KRW']

        spending_cat = spreadsheet_df.groupby('Category')[spending_cols].sum().reset_index()
        spending_cat['Spending (Conv)'] = spending_cat.apply(
            lambda row: round(row['Spending (USD)'] / usd_rate, 2) + round(row['Spending (KRW)'] / krw_rate, 2), axis=1
        )
        spending_cat = spending_cat.loc[(spending_cat['Category'].isin(spending_cats)) | (spending_cat['Spending (CAD)'] > 0) | (spending_cat['Spending (Conv)'] > 0)].reset_index(drop=True)

        earning_cat = spreadsheet_df.groupby('Category')[earning_cols].sum().reset_index()
        earning_cat['Earning (Conv)'] = earning_cat.apply(
            lambda row: round(row['Earning (USD)'] / usd_rate, 2) + round(row['Earning (KRW)'] / krw_rate, 2), axis=1
        )
        earning_cat = earning_cat.loc[(earning_cat['Category'].isin(earning_cats)) | (earning_cat['Earning (CAD)'] > 0) | (earning_cat['Earning (Conv)'] > 0)].reset_index(drop=True)

        spending_category_barplots(sheet_title, spending_cat, purpose='personal')
        spending_category_barplots(sheet_title, spending_cat, purpose='sharing')

        earning_category_barplots(sheet_title, earning_cat, purpose='personal')
        earning_category_barplots(sheet_title, earning_cat, purpose='sharing')

    else:
        if len(spreadsheet['values'][0] < len(col_names)):
            print("Less columns are detected. Adjust your spreadsheet before execution")
        else:
            print("More columns are detected. Adjust your spreadsheet before execution")
