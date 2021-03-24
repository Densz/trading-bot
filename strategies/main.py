from pprint import pprint
import talib.abstract as ta

RSI_LOWER_LEVEL = 30
RSI_MIDDLE_LEVEL = 100


class Strategy:
    main_currency = 'USDT'
    amount_allocated = 1000

    timeframe = "1h"
    tickers = ["BTC/USDT",
               "DOT/USDT",
               "LINK/USDT",
               "LTC/USDT",
               "BCH/USDT",
               "ATOM/USDT",
               "SXP/USDT"]

    def __init__(self):
        print("[STRATEGY] Bollinger bands strategy")
        pass

    def on_tick(self, tickers):
        pass

    def on_new_candle(self, df, tick):
        print("Tick: ", tick)
        df = self._add_indicators(df)
        print(df.tail(3))

    def _add_indicators(self, df):
        df["RSI"] = ta.RSI(df["close"])

        macd = ta.MACD(df, window_fast=12, window_slow=26)
        df['macd'] = macd['macd']
        df['macdsignal'] = macd['macdsignal']
        df['macdhist'] = macd['macdhist']

        df['sma200'] = ta.SMA(df, timeperiod=200)

        return df
