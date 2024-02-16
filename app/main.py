from fastapi import FastAPI

import yfinance as yf

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

    return {"Hello": results.to_string()}
