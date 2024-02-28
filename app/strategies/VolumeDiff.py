from backtesting import Strategy

import pendulum

import pandas as pd

from typing import Dict
from ..utils.TradingCalendarUtils import TradingCalendarUtils

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
                    TradingCalendarUtils.getSessionDateXSessions(
                        trade.entry_time.date(), self.timeframeLen - 1
                    ).strftime("%Y-%m-%d")
                )

                # print(trade.entry_time.date())

                if not hasattr(trade, "exit_date"):
                    # print("entry_time =", trade.entry_time.date())
                    # print("dateInFuture =", dateInFuture)

                    self.count += 1

                    lastTwo = self.data.df.tail(2)

                    trade.real_entry_date = lastTwo.index.values[0]
                    trade.real_entry_price = lastTwo.at[trade.real_entry_date, "Close"]
                    trade.real_volume = lastTwo.at[trade.real_entry_date, "Volume"]

                    # print("trade.real_entry_price =", trade.real_entry_price)

                    # print("trade.entry_time =", trade.entry_time)
                    # print("trade_real_entry_date =", trade.real_entry_date)
                    trade.exit_date = dateInFuture

                if trade.exit_date == today.strftime("%Y-%m-%d"):
                    trade.close()

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
