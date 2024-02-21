from backtesting import Strategy

import pendulum


class VolumeDiff(Strategy):
    name = "VolumeDiff"
    timeframeLen = 4

    def init(self):
        print("Hello World")

    def next(self):
        print("num of data points", len(self.data))

        if len(self.data.df) > self.timeframeLen:
            lastXValues = self.data.df.tail(self.timeframeLen)

            lastTwo = lastXValues[self.timeframeLen // 2 :]
            twoPrior = lastXValues[0 : self.timeframeLen // 2]

            print("lastTwo =", lastTwo)
            print("twoPrior =", twoPrior)

            shouldBuy = True

            for _, row in lastTwo.iterrows():
                for _, row1 in twoPrior.iterrows():
                    if row["Volume"] < row1["Volume"]:
                        shouldBuy = False
                        break

            print("trades =", len(self.trades))

            if shouldBuy:
                print("bought something")
                self.buy()

            now = pendulum.now()

            for trade in self.trades:
                entryTime = pendulum.from_timestamp(trade.entry_time.timestamp())

                print(
                    "trade.entry_time =",
                    pendulum.from_timestamp(trade.entry_time.timestamp()),
                )

                # entryTime = pendulum(trade.entry_time)

                # TODO: Create tool to get
                if entryTime.diff(now).in_days() >= self.timeframeLen:
                    print("close out trade position")
                    trade.close()

                    pendulum.now()
