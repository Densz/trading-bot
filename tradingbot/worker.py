import time
from tradingbot.types import Tick
from typing import Dict, TypedDict
from tradingbot.database import Database
import pandas as pd
from datetime import datetime
from tradingbot.exchange import Exchange

from strategies.main import Strategy
from pprint import pprint

THROTTLE_SECS = 5  # sec


class Worker:
    def __init__(self, config, exchange: Exchange) -> None:
        self._exchange = exchange
        self._config = config
        self._strategy = Strategy(exchange)
        balance = self._exchange.get_balance(self._strategy.main_currency)
        print("[AVAILABLE BALANCE]", balance, self._strategy.main_currency)

        self._last_throttle_time = 0

    # ✅
    def start(self):
        while True:
            self._throttle()

    # ✅
    def _run_bot(self):
        try:
            tickers = self._strategy.tickers
            timeframe = self._strategy.timeframe

            # Call Strategy.on_new_candle()
            for tick in tickers:
                tick_info = self._exchange.fetch_ticker(tick)
                dataframe = self._exchange.fetch_ohlcv(tick, timeframe)
                # Always remove the last row of the dataframe otherwise
                # the last candle won't be a finished candle
                dataframe = dataframe[:-1]
                current_tick: Tick = {
                    'symbol': tick_info['symbol'],
                    'high': tick_info['high'],
                    'low': tick_info['low'],
                    'open': tick_info['open'],
                    'close': tick_info['close'],
                    'baseVolume': tick_info['baseVolume'],
                }
                self._strategy.on_tick(dataframe, current_tick)
        except ValueError:
            print("Fail: _run_bot() trying again...")

    # ✅
    def _throttle(self):
        self._last_throttle_time = time.time()
        self._run_bot()
        time_passed = time.time() - self._last_throttle_time
        sleep_duration = max(THROTTLE_SECS - time_passed, 0.0)
        print(f"[{datetime.fromtimestamp(self._last_throttle_time)}] Throttling: sleep for {sleep_duration:.2f}s, "
              f"last iteration took {time_passed:.2f}s.")
        time.sleep(sleep_duration)
