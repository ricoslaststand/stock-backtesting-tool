from backtesting import Strategy

import pendulum

import pandas as pd

from typing import Dict
import app.utils.TradingCalendarUtils as TradingCalendarUtils


def SMA(array, n):
    """Simple moving average"""
    return pd.Series(array).rolling(n).mean()


class VolumeDiff(Strategy):
    name = "VolumeDiff"
    timeframeLen = 4
    exitDays: Dict[str, str]
    margin = 1.10
    count = 0

    def init(self):
        self.exitDays = {}
        self.maVol90 = self.I(SMA, self.data.Volume, 90)
        self.maVol2 = self.I(SMA, self.data.Volume, 2)

    def next(self):
        # print("\n\n")

        if len(self.data.df) > self.timeframeLen:
            lastXValues = self.data.df.tail(self.timeframeLen)

            lastTwo = lastXValues[self.timeframeLen // 2 :]
            twoPrior = lastXValues[0 : self.timeframeLen // 2]

            shouldBuy = self.__checkStrategy__(lastTwo, twoPrior)

            if shouldBuy:
                self.buy()

            date = pd.Timestamp(self.data.df.tail(1).index.values[0])
            today = pendulum.from_timestamp(date.timestamp())

            for trade in self.trades:
                dateInFuture = (
                    TradingCalendarUtils.TradingCalendarUtils.getSessionDateXSessions(
                        trade.entry_time.date(), self.timeframeLen
                    ).strftime("%Y-%m-%d")
                )

                if not hasattr(trade, "exit_date"):
                    self.count += 1

                    # print("trade.entry_time =", trade.entry_time.date())
                    # print("today =", today)
                    trade.exit_date = dateInFuture
                    # print("self.count =", self.count)
                    # print("trade.exit_date =", trade.exit_date)

                if trade.exit_date == today.strftime("%Y-%m-%d"):
                    trade.close()

        # print("\n\n")

    def __checkStrategy__(self, lastTwo: pd.DataFrame, twoPrior: pd.DataFrame) -> bool:
        for _, row in lastTwo.iterrows():
            for _, row1 in twoPrior.iterrows():
                if row["Volume"] < row1["Volume"]:
                    return False

        #
        lastTwoVolumeSum = 0
        twoPriorVolumeSum = 0

        for _, row in lastTwo.iterrows():
            lastTwoVolumeSum += row["Volume"]

        for _, row in twoPrior.iterrows():
            twoPriorVolumeSum += row["Volume"]

        if (lastTwoVolumeSum / twoPriorVolumeSum) < self.margin:
            return False

        if (
            self.maVol2 is None
            or self.maVol90 is None
            or (self.maVol2 / self.maVol90) <= 0.8
        ):
            return False

        return True
