from abc import abstractmethod
from tradingbot.customtypes import Tick
from typing import Any, Dict, List, Optional, TYPE_CHECKING
import pandas as pd

if TYPE_CHECKING:
    from tradingbot.bot import Bot


class Exchange:
    def __init__(self, bot) -> None:
        self._columns = ["date", "open", "high", "low", "close", "volume"]
        self.bot: Bot = bot

    @abstractmethod
    def create_sell_order(
        self,
        symbol: str,
        strategy: str,
        timeframe: str,
        price: float,
        trade_id: Optional[int] = None,
        reason: str = "",
    ):
        raise BaseException(
            "ERROR: create_sell_order() method should be overridden, or it is not implemented"
        )

    @abstractmethod
    def create_buy_order(
        self,
        symbol: str,
        strategy: str,
        timeframe: str,
        amount: float,
        price: float,
        data: Dict[str, Any] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        is_long: bool = True,
    ) -> bool:
        raise BaseException(
            "ERROR: create_buy_order() method should be overridden, or it is not implemented"
        )

    @abstractmethod
    def fetch_current_ohlcv(self, tick: str) -> Tick:
        raise BaseException(
            "ERROR: fetch_current_ohlcv() method should be overridden, or it is not implemented"
        )

    @abstractmethod
    def fetch_historic_ohlcv(
        self, symbol: str, timeframe: str, with_live_bar: Optional[bool] = False
    ) -> pd.DataFrame:
        raise BaseException(
            "ERROR: fetch_historic_ohlcv() method should be overridden, or it is not implemented"
        )

    # Get balance available in the main currency on Binance
    # Example response: 945.123 (of the main currency)
    @abstractmethod
    def get_balance(self, symbol: str) -> float:
        raise BaseException(
            "ERROR: get_balance() method should be overridden, or it is not implemented"
        )

    @abstractmethod
    def get_all_balances(self) -> Dict[str, Dict[str, Any]]:
        raise BaseException(
            "ERROR: get_all_balances() method should be overridden, or it is not implemented"
        )

    # Return the last close price of the tickers in the array
    # Example response: {
    #   "DOGE/USDT": 0.09213,
    #   "BTC/USDT": 0.12312
    # }
    @abstractmethod
    def get_tickers(self, symbols: List[str]) -> Dict[str, float]:
        raise BaseException(
            "ERROR: get_tickers() method should be overridden, or it is not implemented"
        )

    @abstractmethod
    def get_tradable_balance(self) -> float:
        raise BaseException(
            "ERROR: get_tradable_balance() method should be overridden, or it is not implemented"
        )

    @abstractmethod
    def get_trading_fees(self) -> float:
        raise BaseException(
            "ERROR: get_trading_fees() method should be overridden, or it is not implemented"
        )

    @abstractmethod
    def get_market_symbols(self):
        raise BaseException(
            "ERROR: get_market_symbols() method should be overridden, or it is not implemented"
        )

    @abstractmethod
    def check_pending_orders(self) -> None:
        raise BaseException(
            "ERROR: check_pending_orders() method should be overridden, or it is not implemented"
        )

    def trigger_stoploss_takeprofit(self, symbol: str, ohlc, timeframe: str) -> None:
        open_orders = self.bot.database.get_open_orders(
            symbol=symbol, timeframe=timeframe
        )
        if open_orders == None:
            return
        for order in open_orders:
            if order.initial_stop_loss and ohlc["close"] <= order.initial_stop_loss:
                self.create_sell_order(
                    symbol=order.symbol,
                    strategy=order.strategy,
                    timeframe=timeframe,
                    price=ohlc["close"],
                    trade_id=order.id,
                    reason="Stoploss",
                )
                return
            if order.current_stop_loss and ohlc["close"] <= order.current_stop_loss:
                self.create_sell_order(
                    symbol=order.symbol,
                    strategy=order.strategy,
                    timeframe=timeframe,
                    price=ohlc["close"],
                    trade_id=order.id,
                    reason="Ajusted stoploss",
                )
                return
            if order.take_profit and ohlc["close"] >= order.take_profit:
                self.create_sell_order(
                    symbol=order.symbol,
                    strategy=order.strategy,
                    timeframe=timeframe,
                    price=ohlc["close"],
                    trade_id=order.id,
                    reason="Takeprofit",
                )
                return