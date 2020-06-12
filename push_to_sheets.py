import pygsheets
from key import gsheet_id
import os
from dividend_tracker import *


def get_new_data() -> pd.DataFrame:
    """ Parses DataFrame and extract new data based on last tracked date
    for dividend payouts.

    :return: new DataFrame to push to GSheets
    """

    # TODO: create subset of dataframe to push to Gsheets

    stock_labels = key_stock_labels()
    tracked_date = last_tracked_date()

    for i, (k, v) in enumerate(stock_labels.items()):
        filename = f"{check_make_dir()}\\{v['name']}_dividends.csv"
        df = pd.read_csv(filename)
        for j in range(len(df.index)):
            df.loc[j, 'Date'] = get_epoch(0)
            df.query('Date' > tracked_date[k])
            '''
            if df.loc[j, 'Date'] > tracked_date[k]:
                print('Entered')
                df = 
                df = df[j:, ['Stock', 'Date', 'Dividend/Unit', 'Total Dividend/SGD']]
                df.loc[j, 'Date'] = get_date(df.loc[j, 'Date'])
            '''

    print(df)
    return df


def push_sheets() -> None:
    """ Reads csv file into pandas DataFrame and uploads into Google Sheets.
    Appends data to last row of sheets.
    """

    # TODO: accept argument of type DataFrame based on get_new_data() to push to Gsheets

    json_file = f"{os.getcwd()}\\file.json"
    gc = pygsheets.authorize(service_account_file=json_file)
    stock_labels = key_stock_labels()

    for i, (k, v) in enumerate(stock_labels.items()):
        filename = f"{check_make_dir()}\\{v['name']}_dividends.csv"
        df = pd.read_csv(filename)
        url = "https://docs.google.com/spreadsheets/d/1aaFvn9Pp2-YrDtm6I_kLh3POTpPtIZa6B4wMeKmQHf8/edit#gid=0"
        sh = gc.open_by_url(url)

        if len(df.index) > 0:
            wks = sh[0]
            cells = wks.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')
            last_row = len(cells)
            wks.set_dataframe(df, start=f"A{last_row + 1}", copy_head=False)
            print(f"Finished uploading {v['name']}_dividends.csv")
