#!/usr/bin/env python
import app

from datetime import date


def main():
    """Run administrative tasks."""
    print("Hello World")
    app.tcUtils.TradingCalendarUtils.getLastXSessions(
        date.fromisoformat("2020-03-19"), 10
    )


if __name__ == "__main__":
    main()
