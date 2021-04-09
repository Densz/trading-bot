import time
import asyncio
import ccxt
from pandas.core.frame import DataFrame
from datetime import datetime

from strategies.main import Strategy
from pprint import pprint

THROTTLE_SECS = 5  # sec


class Worker:
    def __init__(self, bot) -> None:
        self.bot = bot

        self.strategy = Strategy(
            self.bot.exchange, self.bot.database, self.bot.telegram
        )
        self._last_throttle_time = 0

    # ✅
    def start(self):
        while True:
            asyncio.get_event_loop().run_until_complete(self._throttle())

    # ✅
    async def _run_bot(self):
        tradable_balance = await self.bot.exchange.get_tradable_balance()
        print(
            f"[TRADABLE BALANCE] {tradable_balance:.2f} {self.bot.strategy.main_currency}"
        )

        if self.bot.config["paper_mode"] == False:
            balance = await self.bot.exchange.get_balance(
                self.bot.strategy.main_currency
            )
            print(
                f"[BALANCE ON BINANCE] {balance:.2f} {self.bot.strategy.main_currency}"
            )
        try:
            if hasattr(self.bot.exchange, "check_pending_orders"):
                await self.bot.exchange.check_pending_orders()

            tickers = self.bot.strategy.tickers
            timeframe = self.bot.strategy.timeframe

            for tick in tickers:
                tick_details = await self.bot.exchange.fetch_current_ohlcv(tick)
                dataframe: DataFrame = await self.bot.exchange.fetch_historic_ohlcv(
                    tick, timeframe
                )
                # Always remove the last row of the dataframe otherwise
                # the last candle won't be a finished candle
                dataframe = dataframe[:-1]

                if hasattr(self.bot.exchange, "trigger_stoploss_takeprofit"):
                    await self.bot.exchange.trigger_stoploss_takeprofit(
                        symbol=tick_details["symbol"], ohlc=tick_details
                    )

                await self.strategy.on_tick(dataframe, tick_details)

        except ValueError as e:
            print(str(e))
            print("Fail: _run_bot() trying again...")

    # ✅
    async def _throttle(self):
        self._last_throttle_time = time.time()
        await self._run_bot()
        time_passed = time.time() - self._last_throttle_time
        sleep_duration = max(THROTTLE_SECS - time_passed, 0.0)
        print(
            f"[{datetime.fromtimestamp(self._last_throttle_time)}] Throttling: sleep for {sleep_duration:.2f}s, "
            f"last iteration took {time_passed:.2f}s."
        )
        time.sleep(sleep_duration)
