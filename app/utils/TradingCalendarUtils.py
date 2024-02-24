import exchange_calendars as xcals

from datetime import date
import pandas as pd


class TradingCalendarUtils:
    def getLastXSessions(date: date, num: int, exchange: str = "XNYS"):
        return xcals.get_calendar(exchange).sessions_window(
            date.__format__("%Y-%m-%d"), -1 * num
        )

    def getSessionDateXSessions(
        date: date, num: int, excStr: str = "XNYS"
    ) -> pd.Timestamp:
        exchange = xcals.get_calendar(excStr)

        return exchange.session_offset(
            exchange.date_to_session(date.__format__("%Y-%m-%d"), direction="next"), num
        )
