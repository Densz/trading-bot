from tradingbot.telegram import Telegram
from tradingbot.exchange.binance import Binance
from tradingbot.database import Database
from pandas.core.frame import DataFrame
from tradingbot.types import Tick
import talib.abstract as ta
from pprint import pprint


class Strategy:
    main_currency = "USDT"
    amount_allocated = 1000

    timeframe = "1m"
    tickers = [
        "DOGE/USDT",
        "DOT/USDT",
        "LINK/USDT",
        "LTC/USDT",
        "BCH/USDT",
        "ATOM/USDT",
        "SXP/USDT",
        "BTC/USDT",
    ]

    # For backtesting will save the params in DB
    # Could be useful for machine learning testing best parameters for better results
    strategy_params = {
        "id": "sample rsi strategy",  # Should always be here
        "rsi_lower_level": 30,
        "rsi_high_level": 70,
    }

    def __init__(self, bot) -> None:
        self._exchange: Binance = bot.exchange
        self._database: Database = bot.database
        self._telegram: Telegram = bot.telegram

    def add_indicators(self, df: DataFrame) -> DataFrame:
        df["RSI"] = ta.RSI(df["close"])

        macd = ta.MACD(df, window_fast=12, window_slow=26)
        df["macd"] = macd["macd"]
        df["macdsignal"] = macd["macdsignal"]
        df["macdhist"] = macd["macdhist"]

        df["sma200"] = ta.SMA(df, timeperiod=200)

        return df

    async def on_tick(self, df: DataFrame, tick: Tick) -> None:
        limit = 10.5  # USDT
        amount = limit / tick["close"]
        open_trade = self._database.has_trade_open(symbol=tick["symbol"])
        last_bar = df.loc[0]

        # There is no open trade
        if open_trade == None:
            if last_bar["RSI"] < self.strategy_params["rsi_lower_level"]:
                self._exchange.create_buy_order(
                    symbol=tick["symbol"],
                    amount=amount,
                    price=tick["close"],
                    stop_loss=tick["close"] * 0.95,
                    take_profit=tick["close"] * 1.05,
                )
        # When there is open trade
        else:
            if last_bar["RSI"] > self.strategy_params["rsi_high_level"]:
                self._exchange.create_sell_order(
                    symbol=tick["symbol"], price=tick["close"], reason="RSI OVER 55"
                )
        pass
