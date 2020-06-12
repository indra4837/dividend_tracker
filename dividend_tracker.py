import os
import time
import datetime
import pandas as pd
import requests
from key import fcs_key


# TODO: dividend tracker pulling newest update from database
# TODO: appending newest update to GSheets (online database)


def check_make_dir() -> str:
    """ Checks if dir exists and creates it.
    To hold csv_file

    :return: Directory name '../Overall-Dividends'
    """
    directory = f"{os.getcwd()}\\Overall-Dividends"
    if not os.path.exists(directory):
        os.mkdir(directory)

    return directory


def check_file(filename) -> bool:
    """ Checks if file exists in the directory stated

    :return: true if file exists in directory
    """
    if os.path.exists(f"{check_make_dir()}\\{filename}"):
        return True
    else:
        return False


def last_tracked_date() -> dict:
    """ Return dict containing last tracked date for each dividend

    :return: dict of stock labels and the last tracked date for dividend payout
    """
    tracked_date = {}
    stock_data = key_stock_labels()
    for k, v in stock_data.items():
        tracked_date[k] = get_epoch(-100)

    return tracked_date


def key_stock_labels() -> dict:
    """ Define stock data structure

    :param option: Selects either from start of from current date
    :return: dict of stock labels based on user choice
    """
    stock_start = {'ES3': {'name': 'STI_ETF', 'bought': '1591228800', 'units': 600.0, 'currency': 'SGD'},
                   'BUOU': {'name': 'Fraser_L&C_Trust', 'bought': '1591228800', 'units': 2759.0, 'currency': 'SGD'},
                   'D05': {'name': 'DBS', 'bought': '1589328000', 'units': 100.0, 'currency': 'SGD'},
                   'BTOU': {'name': 'Manulife_USD_REIT', 'bought': '1508198400', 'units': 3500.0, 'currency': 'USD'},
                   'B73': {'name': 'Global_Investments', 'bought': '1494806400', 'units': 10821, 'currency': 'SGD'},
                   '558': {'name': 'UMS', 'bought': '1520812800', 'units': 1500, 'currency': 'SGD'},
                   'BN2': {'name': 'Valuetronics', 'bought': '1549843200', 'units': 4000, 'currency': 'HKD'}}

    return stock_start


def get_date(epoch_date: int) -> datetime:
    """ Converts normal.

    :return: normal date
    """

    return datetime.datetime.fromtimestamp(epoch_date).now().date()


def get_epoch(day_diff: int) -> int:
    """ Converts normal date to epoch date including time-difference from today's date.

    :param day_diff: number of day difference from today's date
    :return: epoch timestamp
    """
    today_date = datetime.datetime.now().date() + datetime.timedelta(days=day_diff)
    dt = datetime.datetime.strptime(str(today_date), '%Y-%m-%d')
    epoch_today = int(time.mktime(dt.timetuple()))

    return epoch_today


def download_write_csv() -> None:
    """ Downloads csv file from yahoo.finance and store locally for analysis
    """
    # TODO: always overwrite downloads to refresh and obtain new data
    stock = key_stock_labels()

    epoch_date = get_epoch(0)
    for k, v in stock.items():
        url = f"https://query1.finance.yahoo.com/v7/finance/download/{k}.SI?period1={v['bought']}&period2={epoch_date}&interval=1d&events=div"
        response = requests.get(url)
        filename = f"{v['name']}_dividends.csv"
        if check_file(filename):
            print(f"{filename} already exists")
            continue
        else:
            with open(f"{check_make_dir()}\\{filename}", 'wb') as csv_file:
                csv_file.write(response.content)
            print(f"Published {check_make_dir()}\\{filename}")


def currency_converter(foreign_currency: list) -> dict:
    """ Converts the amount from respective currency to SGD using FCSAPI.

    :param foreign_currency: List of foreign currencies to convert
    :return: Total amount in SGD
    """
    sgd = 'SGD'
    currency_conversions = {}
    for i in foreign_currency:
        url = f"https://fcsapi.com/api-v2/forex/converter?symbol={i}/{sgd}&amount=1&access_key={fcs_key}"
        response = requests.get(url).json()
        currency_conversions[i] = float(response['response']['price_1x_SGD'])

    return currency_conversions


def calculate_dividend_received() -> None:
    """ Calculates dividend received based on number of units
    and dividends payout
    """

    stock = key_stock_labels()
    foreign_currency = []

    for k, v in stock.items():
        if not v['currency'] == 'SGD':
            foreign_currency.append(v['currency'])

    # creates dict of currency conversions to be used later
    currency_conversions = currency_converter(foreign_currency)

    for k, v in stock.items():
        filename = f"{check_make_dir()}\\{v['name']}_dividends.csv"
        df = pd.read_csv(filename)

        if not v['name'] in df:  # Labels each row with stock name for future analysis
            df.insert(loc=0, column=v['name'], value=v['name'])
        if not 'Total Dividends/SGD' in df:  # checks if Total Dividends/SGD column already in DataFrame
            df['Total Dividends/SGD'] = 0  # creates column

        for i in range(len(df.index)):
            # Calculate total dividends if not calculated
            if df.at[i, 'Total Dividends/SGD'] == 0:
                if v['currency'] == 'SGD':
                    total_div = df.loc[i, 'Dividends'] * v['units']
                    df.loc[i, 'Total Dividends/SGD'] = total_div
                else:  # do conversion to SGD
                    total_div = df.loc[i, 'Dividends'] * v['units']
                    df.loc[i, 'Total Dividends/SGD'] = total_div * (currency_conversions[v['currency']])

        df.to_csv(filename, index=False)
