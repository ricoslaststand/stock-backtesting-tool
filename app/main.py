from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import HTMLResponse

from typing import Union

import yfinance as yf

import json

import requests

from fastapi.templating import Jinja2Templates

from pandas_datareader import data as pdr

# download dataframe

from .strategies.VolumeDiff import VolumeDiff

from backtesting import Backtest

from .clients.StockClient import StockClient

yf.pdr_override()

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

stocksClient = StockClient


@app.get("/")
def read_root(ticker_symbol: str = "SPY"):
    data = pdr.get_data_yahoo(ticker_symbol, start="2023-03-01", end="2024-03-01")

    if len(data) == 0:
        return {"error": "There is no stock data for this time range."}

    bt = Backtest(
        data, VolumeDiff, cash=10000000000, commission=0.002, exclusive_orders=False
    )

    results = bt.run()

    return json.loads(results.to_json())


def filterTickerSymbol(stock, tickerSymbol):
    return stock["Name"].lower() in tickerSymbol


def getListOfStocks(tickerSymbol: str | None = None):
    stockResponse = requests.get(
        "https://pkgstore.datahub.io/core/s-and-p-500-companies/constituents_json/data/297344d8dc0a9d86b8d107449c851cc8/constituents_json.json"
    )

    if not stockResponse.ok:
        return {"error": "Unable to fetch stocks data"}

    def filterTickerSymbol(stock):
        return stock["Name"].startswith(tickerSymbol)

    stocks = None

    if tickerSymbol:
        stocks = filter(filterTickerSymbol, stockResponse.json())
    else:
        stocks = stockResponse.json()

    return stocks


@app.get("/stocks", response_class=HTMLResponse)
def read_stocks(request: Request, ticker_symbol: Union[str, None] = None):
    stocks = getListOfStocks(ticker_symbol)

    context = {"request": request, "stocks": stocks}

    response = templates.TemplateResponse("stocks.html", context)

    return response


@app.get("/stocks-list")
def get_stocks_list(tickerSymbol: str | None = None):
    stocks = getListOfStocks(tickerSymbol)

    print("ticker_symbol =", tickerSymbol)

    return {"stocks": stocks}


@app.get("/strategies")
def read_strategies():
    arr = []

    for strategy in [VolumeDiff]:
        arr.append({"name": strategy.name, "description": "Stuff goes on."})

    return {"strategies": arr}
