from strategies.main import Strategy
import pandas as pd
from typing import Optional

from tradingbot.exchange import Exchange
from tradingbot.database import Database


class Oanda(Exchange):
    def __init__(self, config, database: Database, strategy: Strategy) -> None:
        self._api: None
        self._config = config

    async def fetch_symbol(self, tick: str):
        print("fetch_symbol on Oanda")
        return []

    async def fetch_ohlcv(self, tickers, timeframe) -> pd.DataFrame:
        pass

    async def get_balance(self, currency):
        pass

    async def create_buy_order(
        self, symbol: str,
        amount: float,
        price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
    ):
        pass

    def update_order(self, order_id, stop_loss: None, take_profit: None):
        pass

    def create_sell_order(self, order_id, at_price):
        pass

    def get_trading_fees(self):
        return 0.001

    def get_market_symbols(self):
        pass

    async def close_connection(self):
        pass
