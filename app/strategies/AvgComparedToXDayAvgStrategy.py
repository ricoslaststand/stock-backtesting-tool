import backtrader as bt


class AvgComparedToXDayAvgStrategy(bt.Strategy):
    name = "AvgComparedToXDayAvgStrategy"

    def __init__(self):
        self.sma = bt.SimpleMovingAverage(period=15)

    def next(self):
        if self.sma > self.data.close:
            # Do something
            pass

        elif self.sma < self.data.close:
            # Do something else
            pass
