from pydantic import BaseModel, Field

from decimal import Decimal
import datetime


class Stock(BaseModel):
    name: str
    sector: str
    symbol: str


class StockClosedTrade(BaseModel):
    ticker_symbol: str
    entry_time: datetime.datetime
    exit_time: datetime.datetime
    trade_duration: Decimal = Field(max_digits=5, decimal_places=1)
    profit_percentage: Decimal = Field(max_digits=5, decimal_places=1)
