import time
import asyncio
import ccxt
import sys
from pandas.core.frame import DataFrame
from datetime import datetime

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tradingbot.bot import Bot

THROTTLE_SECS = 5  # sec


class Worker:
    def __init__(self, bot: "Bot") -> None:
        self.bot: "Bot" = bot
        self.strategy = self.bot.strategy(bot)
        self._last_throttle_time = 0

    def start(self):
        while True:
            asyncio.get_event_loop().run_until_complete(self._throttle())

    async def _run_bot(self):
        # tradable_balance = self.bot.exchange.get_tradable_balance()
        # print(
        #     f"[TRADABLE BALANCE] {tradable_balance:.2f} {self.bot.strategy.main_currency}"
        # )
        if self.bot.config["paper_mode"] == False:
            balance = self.bot.exchange.get_balance(self.bot.strategy.main_currency)
            print(
                f"[BALANCE ON BINANCE] {balance:.2f} {self.bot.strategy.main_currency}"
            )
        try:
            if hasattr(self.bot.exchange, "check_pending_orders"):
                await self.bot.exchange.check_pending_orders()

            tickers = self.bot.strategy.tickers

            for (tick, timeframe) in tickers:
                print(
                    "\033[34m---> Tick:", tick, "|| Timeframe:", timeframe, "\033[39m"
                )
                tick_details = await self.bot.exchange.fetch_current_ohlcv(tick)
                dataframe: DataFrame = await self.bot.exchange.fetch_historic_ohlcv(
                    tick, timeframe
                )
                # Always remove the last row of the dataframe otherwise
                # the last candle won't be a finished candle
                dataframe = dataframe[:-1]

                if hasattr(self.bot.exchange, "trigger_stoploss_takeprofit"):
                    self.bot.exchange.trigger_stoploss_takeprofit(
                        symbol=tick_details["symbol"],
                        ohlc=tick_details,
                        timeframe=timeframe,
                    )
                df_with_indicators = self.strategy.add_indicators(dataframe)
                sorted_df = df_with_indicators.sort_values(by="date", ascending=False)
                sorted_df.reset_index(inplace=True)
                del sorted_df["index"]
                self.strategy.on_tick(
                    sorted_df,
                    tick_details,
                    info={"symbol": tick, "timeframe": timeframe},
                )
        except ccxt.ExchangeNotAvailable:
            msg = "ERROR: Binance Exchange not available trying again..."
            print(msg)
            self.bot.telegram.send_message(msg)
            time.sleep(10)
        except:
            msg = "ERROR: An error occured: " + str(sys.exc_info()[0])
            print(msg)
            self.bot.telegram.send_message(msg)
            print("ERROR: _run_bot() trying again...")

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
