from abc import abstractmethod
from tradingbot.customtypes import Tick
from pandas.core.frame import DataFrame
from tradingbot.chat import Telegram
from tradingbot.database import Database
from tradingbot.exchange import Exchange
from typing import List, Tuple


class IStrategy:
    main_currency: str
    amount_allocated: int
    tickers: List[Tuple[str, str]]

    def __init__(self, bot) -> None:
        self.exchange: Exchange = bot.exchange
        self.database: Database = bot.database
        self.telegram: Telegram = bot.telegram

    @abstractmethod
    def add_indicators(self, df: DataFrame, tick: Tick) -> DataFrame:
        """
        Populate indicators in there
        """

    @abstractmethod
    def on_tick(self, df: DataFrame, tick: Tick, info) -> None:
        """
        Everytime the price of the symbol listed on the attribute tickers
        the function on_tick will be called
        """