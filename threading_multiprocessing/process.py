import os
import json
import pandas as pd
import yfinance as yf

from pathlib import Path
from dotenv import load_dotenv,find_dotenv
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor


BASE_DIR = Path(__file__).resolve().parent


load_dotenv(find_dotenv())


def read_dates(file_name):

    dates = pd.read_csv(
        BASE_DIR / file_name,
        header=None
    )

    return pd.to_datetime(dates[0])


def get_stock_changes(stock_config):

    ticker = stock_config["stock_name"]
    file_name = stock_config["input"]

    print(f"Starting {ticker}")

    dates = read_dates(file_name)

    start = dates.min() - timedelta(hours=2)
    end = dates.max() + timedelta(hours=2)

    data = yf.Ticker(ticker).history(
        start=start,
        end=end,
        interval="1h"
    )

    if data.empty:
        print(f"No data for {ticker}")
        return pd.DataFrame()

    data.index = data.index.tz_convert("UTC").tz_localize(None)

    data["percentage_change"] = data["Close"].pct_change() * 100

    if ticker in os.getenv("HOURLY_STOCKS"):
        requested_hours = dates.dt.floor("h")
    else:
        data.index = data.index.round("30min")
        requested_hours = dates.dt.ceil("30min")

    results = data[data.index.isin(requested_hours)].copy()

    results["hour"] = results.index
    results["stock_type"] = ticker

    print(f"Finished {ticker}: {len(results)} results")

    return results[
        ["hour", "stock_type", "percentage_change"]
    ]


def main():

    configs = [
        json.loads(os.environ["BITCOIN_DATES"]),
        json.loads(os.environ["GOOGLE_DATES"]),
        json.loads(os.environ["AMAZON_DATES"])
    ]

    destination = BASE_DIR / os.environ["DESTINATION_FILE"]

    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(get_stock_changes, configs))

    results = [df for df in results if not df.empty]

    if results:
        final_df = pd.concat(results, ignore_index=True)

        final_df.to_csv(destination, index=False)

        print("Results saved successfully")
    else:
        print("No results found")


if __name__ == "__main__":
    main()