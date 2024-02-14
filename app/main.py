from fastapi import FastAPI

import app.strategies.SmaCross as SmaCross

from backtesting import Backtest
from backtesting.test import GOOG

app = FastAPI()


@app.get("/")
def read_root():
    # class SmaCross(Strategy):
    #     n1 = 10
    #     n2 = 20

    #     def init(self):
    #         close = self.data.Close
    #         self.sma1 = self.I(SMA, close, self.n1)
    #         self.sma2 = self.I(SMA, close, self.n2)

    #     def next(self):
    #         if crossover(self.sma1, self.sma2):
    #             self.buy()
    #         elif crossover(self.sma2, self.sma1):
    #             self.sell()

    bt = Backtest(GOOG, SmaCross, cash=10000, commission=0.002, exclusive_orders=True)

    results = bt.run()

    print("numberOfResults =", len(results))

    return {"Hello": results.to_string()}
