from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import HTMLResponse

from typing import Union

import yfinance as yf

import json

import requests
import requests_cache

from fastapi.templating import Jinja2Templates

from pandas_datareader import data as pdr

# download dataframe

from app.strategies.VolumeDiff import VolumeDiff

from backtesting import Backtest

yf.pdr_override()  # <== that's all it takes :-)

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

session = requests.Session()


@app.get("/")
def read_root(ticker_symbol: str = "SPY"):
    data = pdr.get_data_yahoo(ticker_symbol, start="2017-03-01", end="2017-04-30")

    if len(data) == 0:
        return {"error": "There is no stock data for this time range."}

    bt = Backtest(data, VolumeDiff, cash=10000, commission=0.002, exclusive_orders=True)

    results = bt.run()

    return json.loads(results.to_json())


def filterTickerSymbol(stock, tickerSymbol):
    return stock["Name"].lower() in tickerSymbol


def getListOfStocks(tickerSymbol: Union[str, None] = None):
    stockResponse = requests_cache.CachedSession("cache").get(
        "https://pkgstore.datahub.io/core/s-and-p-500-companies/constituents_json/data/297344d8dc0a9d86b8d107449c851cc8/constituents_json.json"
    )

    if not stockResponse.ok:
        return {"error": "Unable to fetch stocks data"}

    def filterTickerSymbol(stock):
        print("stock =", stock)
        print("ticker_symbol =", tickerSymbol)
        return stock["Name"].startswith(tickerSymbol)

    print(stockResponse.json())

    stocks = None

    print("About to filter stocks")

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
def get_stocks_list(tickerSymbol: Union[str, None] = None):
    stocks = getListOfStocks(tickerSymbol)

    print("ticker_symbol =", tickerSymbol)

    return {"stocks": stocks}


# @app.get("/strategies", response_class=HTMLResponse)
# def read_stocks()


@app.get("/strategies")
def read_strategies():
    arr = []

    for strategy in [VolumeDiff]:
        arr.append({"name": strategy.name})

    return {"strategies": arr}
