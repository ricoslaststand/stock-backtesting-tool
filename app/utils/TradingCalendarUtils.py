import exchange_calendars as xcals


class TradingCalendarUtils:
    def getLastXSessions(num: int, exchange: str = "XNYS") -> None:
        xcals.get_calendar()
