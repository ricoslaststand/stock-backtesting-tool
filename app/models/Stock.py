from pydantic import BaseModel


class Stock(BaseModel):
    name: str
    sector: str
    symbol: str
