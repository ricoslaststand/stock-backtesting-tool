from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import HTMLResponse

from typing import Union

import csv

import yfinance as yf

import json

import requests

from fastapi.templating import Jinja2Templates

from pandas_datareader import data as pdr

# download dataframe

from app.strategies.VolumeDiff import VolumeDiff

from backtesting import Backtest

from app.clients.StockClient import StockClient

from app.models.Stock import StockClosedTrade

from app.utils.TradingCalendarUtils import TradingCalendarUtils

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


def getProfitDiff(prevPrice: float, currPrice: float) -> float:
    return (currPrice - prevPrice) / prevPrice


def main() -> None:
    stocks = StockClient.getStocks()

    hits = []
    for stock in stocks:
        data = None
        try:
            data = pdr.get_data_yahoo(
                stock.symbol, start="2023-03-01", end="2024-03-01"
            )
        except Exception:
            continue
        else:
            if data.empty:
                continue

            bt = Backtest(data, VolumeDiff, cash=10000, exclusive_orders=False)

            results = bt.run()

            print("results =", results["_strategy"])

            for trade in results["_trades"].iterrows():
                # print("trade =", trade[1])
                # print("type(trade) =", type(trade))
                # print("trade =", trade[1])
                # print("len(trade) =", len(trade))
                # # print("tickerSymbol =", trade[[1][1]])

                # print("type(trade_duration) =", type(trade[1]["Duration"]))

                entry_time = trade[1]["EntryTime"]
                print("entry_time =", entry_time)
                # prior_stock_entry_time = TradingCalendarUtils.getSessionDateXSessions(entry_time, -1)
                # print("prior_stock_entry_time =", prior_stock_entry_time)

                real_entry_time = TradingCalendarUtils.getSessionDateXSessions(
                    entry_time, -1
                )
                real_exit_time = TradingCalendarUtils.getSessionDateXSessions(
                    real_entry_time, 4
                )

                # print("real_entry_time =", real_entry_time)
                # print("real_exit_time =", real_exit_time)

                # print(data.index.indexer_at_time(real_entry_time))

                entryDate = None
                exitDate = None

                try:
                    entryDate = data.loc[real_entry_time.strftime("%Y-%m-%d")]
                    exitDate = data.loc[real_exit_time.strftime("%Y-%m-%d")]
                except KeyError:
                    continue

                # print("entryDate.name =", entryDate.name)
                # print("type(entryDate.name) =", type(entryDate.name))

                # print("entryDate =", type(entryDate.index.name))
                # print("exitDate =", type(exitDate.index))

                entryPrice = round(entryDate["Close"], 7)
                exitPrice = round(exitDate["Close"], 7)

                hits.append(
                    StockClosedTrade(
                        ticker_symbol=stock.symbol,
                        entry_time=entryDate.name.to_pydatetime(),
                        exit_time=exitDate.name.to_pydatetime(),
                        profit_percentage=round(
                            getProfitDiff(entryPrice, exitPrice) * 100, 1
                        ),
                        trade_duration="",
                        entry_price=entryPrice,
                        exit_price=exitPrice,
                    )
                )

    with open(
        f"stock_hits_timeframeLen_{VolumeDiff.timeframeLen}_days.csv", mode="w"
    ) as stock_hits_file:
        stock_hits_writer = csv.writer(stock_hits_file, delimiter=",")

        stock_hits_writer.writerow(
            [
                "Ticker Symbol",
                "Entry Time",
                "Exit Time",
                "Entry Price",
                "Exit Price",
                "Profit Percentage",
                "Trade Duration",
            ]
        )

        for hit in hits:
            stock_hits_writer.writerow(
                [
                    hit.ticker_symbol,
                    hit.entry_time,
                    hit.exit_time,
                    hit.entry_price,
                    hit.exit_price,
                    hit.profit_percentage,
                    hit.trade_duration,
                ]
            )


main()
