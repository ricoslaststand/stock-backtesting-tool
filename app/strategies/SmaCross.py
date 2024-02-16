from backtesting import Strategy


class SmaCross(Strategy):
    n1 = 10
    n2 = 20
    name = "SmaCross"

    def init(self):
        # close = self.data.Close
        print("Hello World")

    def next(self):
        self.buy()

        # lastTwo = self.data[-2:]
        # twoPrior = self.data[-3:-5]

        # lastTwo[0].v

        # if crossover(self.sma1, self.sma2):
        #     self.buy()
        # elif crossover(self.sma2, self.sma1):
        #     self.sell()
