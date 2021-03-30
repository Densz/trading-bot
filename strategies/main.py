from pandas.core.frame import DataFrame
from tradingbot.types import Tick
from tradingbot.exchange import Exchange
import talib.abstract as ta
from pprint import pprint


class Strategy():
    main_currency = 'USDT'
    amount_allocated = 1000

    timeframe = "1h"
    tickers = ["BTC/USDT",
               #    "DOT/USDT",
               #    "LINK/USDT",
               #    "LTC/USDT",
               #    "BCH/USDT",
               #    "ATOM/USDT",
               #    "SXP/USDT",
               "DOGE/USDT"]

    # For backtesting will save the params in DB
    # Could be useful for machine learning testing best parameters for better results
    strategy_params = {
        'id': 'Bollinger bands strategy',  # Should always be here
        'rsi_lower_level': 30,
        'rsi_high_level': 70
    }

    def __init__(self, exchange: Exchange):
        print(f"[STRATEGY] {self.strategy_params['id']}")
        self._exchange = exchange
        pass

    def _add_indicators(self, df: DataFrame) -> DataFrame:
        df["RSI"] = ta.RSI(df["close"])

        macd = ta.MACD(df, window_fast=12, window_slow=26)
        df['macd'] = macd['macd']
        df['macdsignal'] = macd['macdsignal']
        df['macdhist'] = macd['macdhist']

        df['sma200'] = ta.SMA(df, timeperiod=200)

        return df

    async def on_tick(self, df: DataFrame, tick: Tick) -> None:
        print("Tick: ", tick["symbol"])
        df = self._add_indicators(df)
        print(df.tail(1))
        pprint(tick)
        # test = self._exchange.create_buy_order(
        #     tick['symbol'], 400, 0.032336)
        # pprint(test)
        pass

    def _calculate_take_profit(self):
        pass

    def _calculate_stop_loss(self):
        pass

    def _calculate_amount(self):
        pass

    def _check_if_order_open(self):
        pass
