from pandas.core.frame import DataFrame
from tradingbot.types import Tick
import talib.abstract as ta
from pprint import pprint


class Strategy():
    main_currency = 'USDT'
    amount_allocated = 1000

    timeframe = "1h"
    tickers = ["DOGE/USDT",
               #    "DOT/USDT",
               #    "LINK/USDT",
               #    "LTC/USDT",
               #    "BCH/USDT",
               #    "ATOM/USDT",
               #    "SXP/USDT",
               #    "BTC/USDT"
               ]

    # For backtesting will save the params in DB
    # Could be useful for machine learning testing best parameters for better results
    strategy_params = {
        'id': 'Bollinger bands strategy',  # Should always be here
        'rsi_lower_level': 30,
        'rsi_high_level': 70
    }

    def __init__(self, exchange):
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
        await self._exchange.create_buy_order(
            symbol=tick['symbol'],
            amount=400,
            price=0.032336,
            stop_loss=0.032336 * 0.8,
            take_profit=0.032336 * 1.2
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
