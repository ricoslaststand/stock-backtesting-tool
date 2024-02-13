import backtrader as bt


class AvgComparedToXDayAvgStrategy(bt.Strategy):
    name = "AvgComparedToXDayAvgStrategy"

    def __init__(self):
        self.data = [0]
