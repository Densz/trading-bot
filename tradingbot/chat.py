from tradingbot.utils import calculate_profit
import arrow
from tabulate import tabulate
import re

from telegram import ReplyKeyboardMarkup, ParseMode
from telegram.ext import CommandHandler, Updater
from telegram.ext.dispatcher import Dispatcher

from tradingbot.database import Trade

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from tradingbot.bot import Bot


class Telegram:
    def __init__(self, bot: "Bot") -> None:
        self.bot: Bot = bot

        self._updater: Updater = Updater(self.bot.config["telegram"]["token"])
        self._dispatcher: Dispatcher = self._updater.dispatcher
        self._is_paper_mode: bool = self.bot.config["paper_mode"]

        self._init_keyboard()
        self._add_handler()

        self._updater.start_polling()

    def _init_keyboard(self) -> None:
        reply_markup = ReplyKeyboardMarkup(
            [
                ["/status", "/historic", "/profit"],
                ["/balance", "/forcesell", "/breakeven"],
                ["/info", "/help"],
            ],
            resize_keyboard=True,
        )
        if self.bot.config["telegram"]["enabled"] == True:
            self._updater.bot.send_message(
                chat_id=self.bot.config["telegram"]["chat_id"],
                text=f"<b>🏃 Bot is Trading !</b> <code>{'[Paper mode]' if self._is_paper_mode else '[Live mode]'}</code>",
                reply_markup=reply_markup,
                disable_notification=True,
                parse_mode=ParseMode.HTML,
            )

    def clean(self) -> None:
        self._updater.stop()

    def send_message(self, msg: str) -> None:
        if self.bot.config["telegram"]["enabled"] == True:
            self._updater.bot.send_message(
                chat_id=self.bot.config["telegram"]["chat_id"],
                text=msg,
                disable_notification=True,
                parse_mode=ParseMode.HTML,
            )

    def _add_handler(self):
        handlers = [
            CommandHandler("help", self._help),
            CommandHandler("status", self._status),
            CommandHandler("profit", self._profit),
            CommandHandler("info", self._info),
            CommandHandler("balance", self._balance),
            CommandHandler("forcesell", self._forcesell),
            CommandHandler("historic", self._historic),
            CommandHandler("breakeven", self._breakeven),
        ]
        for handler in handlers:
            self._dispatcher.add_handler(handler)

    def _help(self, update, context) -> None:
        msg = "<b>Available commands:</b>\n"
        msg += "<b>/status</b> get all open trades status\n"
        msg += "<b>/profit</b> get total profit since the start\n"
        msg += "<b>/balance</b> get balance for each symbol in exchange\n"
        msg += "<b>/forcesell [Trade ID]</b> force sell an open order at the current closing price\n"
        msg += "<b>/breakeven [Trade ID]</b> make the trade breakeven by updating the stoploss\n"
        msg += "<b>/historic</b> get historic closed orders\n"
        msg += "<b>/info</b> get strategy information\n"
        self.send_message(msg)

    def _status(self, update, context) -> None:
        open_orders = self.bot.database.get_open_orders()

        if open_orders == None or len(open_orders) == 0:
            return self.send_message("No open orders for the moment yet")

        trading_fee_rate = self.bot.exchange.get_trading_fees()
        trades = []
        open_orders_symbols = []

        for data in open_orders:
            open_orders_symbols.append(data.symbol)

        # Remove duplicates values -> (list(dict.fromkeys(open_orders_symbols))
        open_orders_symbols = list(dict.fromkeys(open_orders_symbols))
        sell_prices = self.bot.exchange.get_tickers(symbols=open_orders_symbols)

        for row in open_orders:
            profit, profit_pct, close_return = calculate_profit(
                amount_available=row.amount_available,
                close_price=sell_prices[row.symbol],
                open_cost=row.open_cost,
                trading_fee_rate=trading_fee_rate,
            )
            trades.append(
                [
                    row.id,
                    row.strategy,
                    row.symbol,
                    self.shorten_date(
                        arrow.get(row.open_date.timestamp()).humanize(
                            only_distance=True
                        )
                    ),
                    f"${row.open_cost:.2f}",
                    f"${profit:.2f} ({(profit_pct * 100):.2f}%)",
                ]
            )
        msg = tabulate(
            trades,
            headers=["ID", "Strat", "Pairs", "Date", "Invested", "Profit"],
            tablefmt="simple",
            stralign="right",
        )
        self.send_message("<b>" + msg + "</b>")

    def _profit(self, update, context) -> None:
        total_profit = 0
        total_profit_pct = 0
        total_profit_win = 0
        total_profit_pct_win = 0
        total_profit_loss = 0
        total_profit_pct_loss = 0
        total_trades = 0
        win_trades = 0
        loss_trades = 0

        db_trades = Trade.select().where(Trade.close_order_status == "closed").execute()

        for row in db_trades:
            total_trades += 1
            if row.profit > 0:
                win_trades += 1
                total_profit_win += row.profit
                total_profit_pct_win += row.profit_pct
            else:
                loss_trades += 1
                total_profit_loss += row.profit
                total_profit_pct_loss += row.profit_pct
            total_profit += row.profit
            total_profit_pct += row.profit_pct

        msg = f"<b>Profit</b>: <code>{total_profit:.2f} {self.bot.strategy.main_currency} ({total_profit_pct:.2f}%)</code>\n"
        msg += f"<b>Total trades count</b>: <code>{total_trades}</code>\n"
        msg += f"<b>Win / Loss</b>: <code>{win_trades} / {loss_trades}</code>\n"
        msg += f"<b>Cumulated Win Profit</b>: <code>{total_profit_win:.2f} {self.bot.strategy.main_currency} ({total_profit_pct_win:.2f}%)</code>\n"
        msg += f"<b>Cumulated Loss Profit</b>: <code>{total_profit_loss:.2f} {self.bot.strategy.main_currency} ({total_profit_pct_loss:.2f}%)</code>\n"
        self.send_message(msg)

    def _historic(self, update, context) -> None:
        trades = []
        db_trades = (
            Trade.select()
            .where(Trade.close_order_status == "closed")
            .order_by(Trade.id.desc())
            .limit(10)
            .execute()
        )
        for row in db_trades:
            is_profit = row.profit > 0
            trades.append(
                [
                    "✅" if is_profit else "❌",
                    row.id,
                    row.strategy,
                    row.symbol,
                    self.shorten_date(
                        arrow.get(row.close_date.timestamp()).humanize(
                            only_distance=True
                        )
                    ),
                    f"${row.profit:.2f} ({(row.profit_pct * 100):.2f}%)",
                ]
            )
        msg = tabulate(
            trades,
            headers=["Res", "ID", "Strat", "Pairs", "Date", "Profit"],
            tablefmt="simple",
            stralign="left",
        )
        self.send_message("<b>" + msg + "</b>")

    def _info(self, update, context) -> None:
        msg = f"<b>Tickers</b>: <code>{self.bot.strategy.tickers}</code>\n"
        msg += f"<b>Amount allocated</b>: <code>{self.bot.strategy.amount_allocated}</code>\n"
        self.send_message(msg)

    def _balance(self, update, context) -> None:
        msg = ""
        balances = self.bot.exchange.get_all_balances()
        for item in balances.items():
            msg += f"\n<b>{item[0]}:</b>\n"
            for data in item[1].items():
                msg += f"{data[0]}: <code>{data[1]}</code>\n"
        self.send_message(msg)

    def _forcesell(self, update, context) -> None:
        if len(context.args) == 0:
            return self.send_message("/forcesell missing arguments")
        arg = context.args[0]
        trade = (
            Trade.select()
            .where(
                Trade.id == arg,
            )
            .execute()
        )
        if len(trade) == 0:
            return self.send_message(f"/forcesell no trade found with id {arg}")
        else:
            if trade[0].close_order_status != None:
                return self.send_message(
                    f"Trade id {arg} is closing or has been closed already"
                )
            sell_price = self.bot.exchange.get_tickers(trade[0].symbol)
            self.bot.exchange.create_sell_order(
                symbol=trade[0].symbol,
                strategy=trade[0].strategy,
                timeframe=trade[0].timeframe,
                price=sell_price[trade[0].symbol],
                trade_id=trade[0].id,
                reason="telegram_force_sell",
            )

    def _breakeven(self, update, context) -> None:
        if len(context.args) == 0:
            return self.send_message("/breakeven missing arguments")
        arg = context.args[0]
        trade = (
            Trade.select()
            .where(
                Trade.id == arg,
            )
            .execute()
        )
        if len(trade) == 0:
            return self.send_message(f"/breakeven no trade found with id {arg}")
        else:
            if trade[0].close_order_status != None:
                return self.send_message(
                    f"Trade id {arg} is closing or has been closed already"
                )
            sell_price = self.bot.exchange.get_tickers(trade[0].symbol)
            if sell_price[trade[0].symbol] < trade[0].open_price:
                return self.send_message(
                    f"Trade {arg} price is below the breakeven price, you can /forcesell it if needed"
                )
            self.bot.database.update_trade(
                trade_id=trade[0].id, stoploss=trade[0].open_price
            )
            self.send_message(f"Trade {arg} stoploss has been set to breakeven price")

    def notify_buy(
        self,
        exchange: str,
        strategy: str,
        symbol: str,
        amount: float,
        open_rate: float,
        stop_loss: Optional[float] = 0,
        take_profit: Optional[float] = None,
    ):
        total_invested = amount * open_rate
        template = [
            [f"🔵 {exchange.title()}", f"Buying {symbol}\n"],
            ["Strategy", f"{strategy}\n"],
            ["Amount", f"{amount}\n"],
            ["Open rate", f"{open_rate}\n"],
            ["Total", f"{total_invested:.2f} USDT\n"],
            ["Stop loss price", f"{stop_loss}\n"],
            ["Take profit price", f"{take_profit if take_profit != None else ''}"],
        ]
        msg = self.format_array_to_msg(template)
        self.send_message(msg)

    def notify_sell(
        self,
        exchange: str,
        strategy: str,
        symbol: str,
        amount: float,
        open_rate: float,
        current_rate: float,
        close_rate: float,
        reason: str,
        profit: float = 0,
        profit_pct: float = 0,
    ):
        icon = "❌ " if profit < 0 else "✅ "
        template = [
            [f"{icon} {exchange.title()}", f"Selling {symbol}\n"],
            ["Strategy", f"{strategy}\n"],
            ["Amount", f"{amount}\n"],
            ["Open rate", f"{open_rate}\n"],
            ["Current rate", f"{current_rate}\n"],
            ["Close rate", f"{close_rate}\n"],
            ["Reason", f"{reason}\n"],
            ["Profit (%)", f"{profit_pct:.2f}%\n"],
            ["Profit (USDT)", f"{profit:.2f} USDT"],
        ]
        msg = self.format_array_to_msg(template)
        self.send_message(msg)

    @staticmethod
    def shorten_date(_date: str) -> str:
        """
        Trim the date so it fits on small screens
        """
        new_date = re.sub("seconds?", "sec", _date)
        new_date = re.sub("minutes?", "min", new_date)
        new_date = re.sub("hours?", "h", new_date)
        new_date = re.sub("days?", "d", new_date)
        new_date = re.sub("^an?", "1", new_date)
        return new_date

    @staticmethod
    def format_array_to_msg(arr):
        msg = ""
        terminal_msg = ""
        for row in arr:
            msg += "<b>" + row[0] + ":</b> " + "<code>" + row[1] + "</code>"
            terminal_msg += row[0] + ": " + row[1]
        print("-------------------------")
        print(terminal_msg)
        print("-------------------------")
        return msg
