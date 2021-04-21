from tradingbot.telegram import Telegram
from tradingbot.exchange.binance import Binance
from tradingbot.database import Database
from pandas.core.frame import DataFrame
from tradingbot.types import Tick
import talib.abstract as ta
from pprint import pprint

RSI_STRATEGY = {
    "id": "RSI",
    "rsi_lower_level": 45,
    "rsi_high_level": 55,
}

RSI_STRATEGY_2 = {
    "id": "RSI2",
    "rsi_lower_level": 55,
    "rsi_high_level": 45,
}


class Strategy:
    """
    MUST HAVE VARIABLES AND FUNCTIONS BELOW
    TO BE ABLE TO RUN THE BOT
    Variables:
        - main_currency
        - amount_allocated
        - tickers
    Functions:
        - __init__
        - add_indicators
        - on_tick

    """

    main_currency = "USDT"
    amount_allocated = 1000

    tickers = [
        ("DOGE/USDT", "1m"),
        ("DOGE/USDT", "15m"),
        ("BNB/USDT", "1m"),
        ("BTC/USDT", "1m"),
    ]

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

    def on_tick(self, df: DataFrame, tick: Tick, info) -> None:
        self._run_strat_1(df, tick, info)
        if tick["symbol"] == "DOGE/USDT" and info["timeframe"] == "15m":
            self._run_strat_2(df, tick, info)
        pass

    """
        CUSTOM FUNCTIONS BELOW
        Examples:
            - Strategy code
            - Risk management
            - Update Stoploss and takeprofit
    """

    def _run_strat_1(self, df, tick, info) -> None:
        print("Run strat 1")
        limit = 13.5  # USDT
        amount = limit / tick["close"]
        open_trade = self._database.has_trade_open(
            symbol=tick["symbol"],
            strategy=RSI_STRATEGY["id"],
            timeframe=info["timeframe"],
        )
        last_bar = df.loc[0]

        # There is no open trade
        if open_trade == None:
            if last_bar["RSI"] < RSI_STRATEGY["rsi_lower_level"]:
                self._exchange.create_buy_order(
                    symbol=tick["symbol"],
                    strategy=RSI_STRATEGY["id"],
                    timeframe=info["timeframe"],
                    amount=amount,
                    price=tick["close"],
                    stop_loss=tick["close"] * 0.95,
                    take_profit=tick["close"] * 1.05,
                )
        # When there is open trade
        else:
            if last_bar["RSI"] > RSI_STRATEGY["rsi_high_level"]:
                self._exchange.create_sell_order(
                    symbol=tick["symbol"],
                    strategy=RSI_STRATEGY["id"],
                    timeframe=info["timeframe"],
                    price=tick["close"],
                    reason="RSI OVER 70",
                )
        pass

    def _run_strat_2(self, df, tick, info) -> None:
        print("Run strat 2")
        limit = 13.5  # USDT
        amount = limit / tick["close"]
        open_trade = self._database.has_trade_open(
            symbol=tick["symbol"],
            strategy=RSI_STRATEGY_2["id"],
            timeframe=info["timeframe"],
        )
        last_bar = df.loc[0]

        # There is no open trade
        if open_trade == None:
            if last_bar["RSI"] > RSI_STRATEGY_2["rsi_lower_level"]:
                self._exchange.create_buy_order(
                    symbol=tick["symbol"],
                    strategy=RSI_STRATEGY_2["id"],
                    timeframe=info["timeframe"],
                    amount=amount,
                    price=tick["close"],
                    stop_loss=tick["close"] * 0.95,
                    take_profit=tick["close"] * 1.05,
                )
        # When there is open trade
        else:
            if last_bar["RSI"] < RSI_STRATEGY_2["rsi_high_level"]:
                self._exchange.create_sell_order(
                    symbol=tick["symbol"],
                    strategy=RSI_STRATEGY_2["id"],
                    timeframe=info["timeframe"],
                    price=tick["close"],
                    reason="RSI UNDER 30",
                )
        pass