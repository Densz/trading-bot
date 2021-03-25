
from typing import TypedDict


class Tick(TypedDict):
    symbol: str
    high: float
    low: float
    open: float
    close: float
    baseVolume: float
