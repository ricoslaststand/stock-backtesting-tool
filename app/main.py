from fastapi import FastAPI

import yfinance as yf

import json

import requests

from pandas_datareader import data as pdr

# download dataframe

from app.strategies.VolumeDiff import VolumeDiff

from backtesting import Backtest

yf.pdr_override()  # <== that's all it takes :-)

app = FastAPI()


@app.get("/")
def read_root(ticker_symbol: str = "SPY"):
    data = pdr.get_data_yahoo(ticker_symbol, start="2017-03-01", end="2017-04-30")

    bt = Backtest(data, VolumeDiff, cash=10000, commission=0.002, exclusive_orders=True)

    results = bt.run()

    print("numberOfResults =", len(results))

    print("results =", results)

    return json.loads(results.to_json())


@app.get("/stocks")
def read_stocks():
    response = requests.get(
        "https://pkgstore.datahub.io/core/s-and-p-500-companies/constituents_json/data/297344d8dc0a9d86b8d107449c851cc8/constituents_json.json"
    )

    if not response.ok:
        return {"error": "Unable to fetch stocks data"}

    return response.json()


@app.get("/strategies")
def read_strategies():
    arr = []

    for strategy in [VolumeDiff]:
        arr.append({"name": strategy.name})

    return {"strategies": arr}
