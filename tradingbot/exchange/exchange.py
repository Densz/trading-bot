from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tradingbot.bot import Bot


class Exchange:
    def __init__(self, bot) -> None:
        self._columns = ["date", "open", "high", "low", "close", "volume"]
        self.bot: Bot = bot

    def trigger_stoploss_takeprofit(self, symbol: str, ohlc, timeframe: str) -> None:
        open_orders = self.bot.database.get_open_orders(
            symbol=symbol, timeframe=timeframe
        )

        if open_orders == None:
            return
        for order in open_orders:
            if order.initial_stop_loss and ohlc["close"] <= order.initial_stop_loss:
                self.create_sell_order(
                    symbol=order.symbol,
                    strategy=order.strategy,
                    timeframe=timeframe,
                    price=ohlc["close"],
                    trade_id=order.id,
                    reason="Stoploss",
                )
                return
            if order.current_stop_loss and ohlc["close"] <= order.current_stop_loss:
                self.create_sell_order(
                    symbol=order.symbol,
                    strategy=order.strategy,
                    timeframe=timeframe,
                    price=ohlc["close"],
                    trade_id=order.id,
                    reason="Ajusted stoploss",
                )
                return
            if order.take_profit and ohlc["close"] >= order.take_profit:
                self.create_sell_order(
                    symbol=order.symbol,
                    strategy=order.strategy,
                    timeframe=timeframe,
                    price=ohlc["close"],
                    trade_id=order.id,
                    reason="Takeprofit",
                )
                return