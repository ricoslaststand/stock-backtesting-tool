#!/usr/bin/env python
from utils.TradingCalendarUtils import TradingCalendarUtils as tcUtils
from clients.StockClient import StockClient

from strategies.VolumeDiff import VolumeDiff
from models.Stock import StockClosedTrade

import yfinance as yf

import csv
from backtesting import Backtest
from datetime import date

from pandas_datareader import data as pdr

yf.pdr_override()


def getProfitDiff(prevPrice: float, currPrice: float) -> float:
    return (currPrice - prevPrice) / prevPrice


def main() -> None:
    stocks = StockClient.getStocks()

    hits = []
    for stock in stocks:
        data = None
        try:
            # TODO: Create separate class to retrieve stock data and return Dataframe
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

                real_entry_time = tcUtils.getSessionDateXSessions(entry_time, -1)
                real_exit_time = tcUtils.getSessionDateXSessions(real_entry_time, 4)

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


def main():
    """Run administrative tasks."""
    print("Hello World")
    tcUtils.getLastXSessions(date.fromisoformat("2020-03-19"), 10)


if __name__ == "__main__":
    main()
