from tradingbot.logger import logger
import time
import asyncio
import ccxt
import sys
import traceback
from pandas.core.frame import DataFrame
from datetime import datetime

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tradingbot.bot import Bot

THROTTLE_SECS = 5  # sec


class Worker:
    def __init__(self, bot: "Bot") -> None:
        self.bot: "Bot" = bot
        self._last_throttle_time = 0

    def start(self):
        while True:
            asyncio.get_event_loop().run_until_complete(self._throttle())

    async def _run_bot(self):
        try:
            if hasattr(self.bot.exchange, "check_pending_orders"):
                self.bot.exchange.check_pending_orders()

            tickers = self.bot.strategy.tickers

            for (tick, timeframe) in tickers:
                logger.info(f"Tick: {tick}, || Timeframe: {timeframe}")
                tick_details = self.bot.exchange.fetch_current_ohlcv(tick)
                dataframe: DataFrame = self.bot.exchange.fetch_historic_ohlcv(
                    tick, timeframe
                )
                if hasattr(self.bot.exchange, "trigger_stoploss_takeprofit"):
                    self.bot.exchange.trigger_stoploss_takeprofit(
                        symbol=tick_details["symbol"],
                        ohlc=tick_details,
                        timeframe=timeframe,
                    )
                df_with_indicators = self.bot.strategy.add_indicators(
                    dataframe, tick_details
                )
                # sorted_df = df_with_indicators.sort_values(by="date", ascending=False)
                # sorted_df.reset_index(inplace=True)
                # del sorted_df["index"]
                self.bot.strategy.on_tick(
                    df_with_indicators,
                    tick_details,
                    info={"symbol": tick, "timeframe": timeframe},
                )
        except ccxt.ExchangeNotAvailable:
            msg = "Binance Exchange not available trying again..."
            logger.error(msg)
            self.bot.telegram.send_message(msg)
            time.sleep(10)
        except:
            traceback.print_exc()
            msg = "An error occured: " + str(sys.exc_info()[0])
            logger.error(msg)
            self.bot.telegram.send_message(msg)
            logger.error("_run_bot() trying again...")

    async def _throttle(self):
        self._last_throttle_time = time.time()
        await self._run_bot()
        time_passed = time.time() - self._last_throttle_time
        sleep_duration = max(THROTTLE_SECS - time_passed, 0.0)
        logger.warning(
            f"Throttling: sleep for {sleep_duration:.2f}s, last iteration took {time_passed:.2f}s."
        )
        time.sleep(sleep_duration)
