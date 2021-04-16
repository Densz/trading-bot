import pandas as pd
from typing import Optional

from tradingbot.exchange import Exchange


class Oanda(Exchange):
    def __init__(self, bot) -> None:
        self.bot = bot
        self._api: None

    async def fetch_current_ohlcv(self, tick: str):
        print("fetch_current_ohlcv on Oanda")
        return []

    async def fetch_historic_ohlcv(self, tickers, timeframe) -> pd.DataFrame:
        pass

    async def get_balance(self, currency):
        pass

    def create_buy_order(
        self,
        symbol: str,
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
