from fastapi import FastAPI

import yfinance as yf
import backtrader as bt

app = FastAPI()


@app.get("/")
def read_root():
    cerebro = bt.Cerebro()
    # cerebro.addstrategy(AvgComparedToXDayAvgStrategy)

    # Add a strategy
    cerebro.addstrategy(bt.Strategy)

    cerebro.broker.setcash(100000)

    # fileName = "YHOO.csv"
    # file = open(fileName, "w")
    # file.close()

    # Create a Data Feed
    data = bt.feeds.PandasData(
        dataname=yf.download("SPY", "2021-06-06", "2021-07-01", auto_adjust=True)
    )
    # Add the Data Feed to Cerebro
    cerebro.adddata(data)
    cerebro.run()
    return {"Hello": cerebro.broker.getvalue()}
