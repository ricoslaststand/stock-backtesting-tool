from models.Stock import Stock

from typing import List

import requests_cache

import datetime as dt
import pandas as pd

import yfinance as yf

from pandas_datareader import data as pdr

yf.pdr_override()

session = requests_cache.CachedSession("stock_cache")


class StockClient:
    dateFormat = "%Y-%m-%d"

    def __init__(self) -> None:
        self.stocks = self.getStocks()

    def getStocks(tickerSymbol: str | None = None) -> List[Stock]:
        stockResponse = session.get(
            "https://pkgstore.datahub.io/core/s-and-p-500-companies/constituents_json/data/297344d8dc0a9d86b8d107449c851cc8/constituents_json.json"
        )

        stocks = []

        def filterTickerSymbol(stock: Stock):
            return stock.symbol.startswith(tickerSymbol)

        for stock in stockResponse.json():
            stocks.append(
                Stock(
                    name=stock["Name"], sector=stock["Sector"], symbol=stock["Symbol"]
                )
            )

        if tickerSymbol:
            stocks = filter(filterTickerSymbol, stocks)

        return stocks

    def getStockMarketData(
        tickerSymbol: str, startDate: dt.date, endDate: dt.date
    ) -> pd.DataFrame | pd.Series:
        return pdr.get_data_yahoo(
            tickerSymbol,
            start=startDate.strftime(StockClient.dateFormat),
            end=endDate.strftime(StockClient.dateFormat),
        )
