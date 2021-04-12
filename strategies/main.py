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
        "id": "Bollinger bands strategy",  # Should always be here
        "rsi_lower_level": 30,
        "rsi_high_level": 70,
    }

    def __init__(
        self, exchange: Binance, database: Database, telegram: Telegram
    ) -> None:
        print(f"\033[34m[STRATEGY] {self.strategy_params['id']}", "\033[39m")
        self._exchange = exchange
        self._database = database
        self._telegram = telegram
        pass

    def _add_indicators(self, df: DataFrame) -> DataFrame:
        df["RSI"] = ta.RSI(df["close"])

        macd = ta.MACD(df, window_fast=12, window_slow=26)
        df["macd"] = macd["macd"]
        df["macdsignal"] = macd["macdsignal"]
        df["macdhist"] = macd["macdhist"]

        df["sma200"] = ta.SMA(df, timeperiod=200)

        return df

    async def on_tick(self, df: DataFrame, tick: Tick) -> None:
        print("\033[34m---> Tick: ", tick["symbol"], "\033[39m")
        df = self._add_indicators(df)
        limit = 10.5  # USDT
        amount = limit / tick["close"]
        open_trade = self._database.has_trade_open(symbol=tick["symbol"])
        last_candle = df.tail(1).to_dict("records")[0]
        print("RSI ->", str(last_candle["RSI"]))
        print("open_trade ->", open_trade != None)

        if last_candle["RSI"] > 50 and last_candle["RSI"] < 55:
            print("Between 50 & 55")

        # There is no open trade
        if open_trade == None:
            if last_candle["RSI"] < 70:
                print("RSI under 10")
                await self._exchange.create_buy_order(
                    symbol=tick["symbol"],
                    amount=amount,
                    price=tick["close"],
                    stop_loss=tick["close"] * 0.95,
                    take_profit=tick["close"] * 1.05,
                )
        # When there is open trade
        else:
            if last_candle["RSI"] > 90:
                print("RSI over 55")
                await self._exchange.create_sell_order(
                    symbol=tick["symbol"], price=tick["close"], reason="RSI OVER 55"
                )
        pass

    def _calculate_take_profit(self):
        pass

    def _calculate_stop_loss(self):
        pass

    def _calculate_amount(self):
        pass

    def _check_if_order_open(self):
        pass
