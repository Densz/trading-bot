import arrow
from tabulate import tabulate
import re

from telegram import ReplyKeyboardMarkup, ParseMode
from telegram.ext import CommandHandler, Updater
from telegram.ext.dispatcher import Dispatcher

from typing import TYPE_CHECKING

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
                ["/status", "/profit", "/daily"],
                ["/balance", "/forcesell", "/help"],
            ],
            resize_keyboard=True,
        )
        self._updater.bot.send_message(
            chat_id=self.bot.config["telegram"]["chat_id"],
            text=f"<b>🏃 Bot is Trading !</b> <code>{'[Paper mode]' if self._is_paper_mode else '[Live mode]'}</code>",
            reply_markup=reply_markup,
            disable_notification=True,
            parse_mode=ParseMode.HTML,
        )

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
            CommandHandler("daily", self._daily),
            CommandHandler("balance", self._balance),
            CommandHandler("forcesell", self._forcesell),
        ]
        for handler in handlers:
            self._dispatcher.add_handler(handler)

    def _help(self, update, context) -> None:
        self.send_message(
            "Available commands:\n/status to get all trades status\n/profit get total profit since the start\n/daily get daily profit\n/balance get current balance in USDT\n/forcesell [ID] sell an open order\n"
        )

    def _status(self, update, context) -> None:
        open_orders = self.bot.database.get_open_orders()

        if open_orders == None or len(open_orders) == 0:
            return self.send_message("No open orders for the moment yet")

        trading_fee_rate = self.bot.exchange.get_trading_fees()
        trades = []
        for row in open_orders:
            sell_price = self.bot.exchange.get_sell_price(row.symbol)
            [profit, profit_pct, close_return] = self.bot.exchange.calculate_profit(
                amount_available=row.amount_available,
                close_price=sell_price,
                open_cost=row.open_cost,
                trading_fee_rate=trading_fee_rate,
            )
            trades.append(
                [
                    row.id,
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
            headers=["ID", "Pairs", "Date", "Invested", "Profit"],
            tablefmt="simple",
            stralign="right",
        )
        self.send_message("<b>" + msg + "</b>")

    def _profit(self, update, context) -> None:
        """
        ROI: Closed trades
        ∙ -3.69307039 USDT (0.18%) (10.67 Σ%)
        ∙ -3.730 USD
        ROI: All trades
        ∙ -55.79919668 USDT (-0.25%) (-15.4 Σ%)
        ∙ -56.357 USD
        Total Trade Count: 62
        First Trade opened: 2 weeks ago
        Latest Trade opened: a day ago
        Win / Loss: 30 / 28
        Avg. Duration: 5:41:57
        Best Performing: SXP/USDT: 11.75%
        """
        self.send_message("/profit not implemented yet")

    def _daily(self, update, context) -> None:
        """
        Daily Profit over the last 7 days:
        Day         Profit USDT      Profit USD    Trades
        ----------  ---------------  ------------  --------
        2021-04-12  0.00000000 USDT  0.000 USD     0 trades
        2021-04-11  0.00000000 USDT  0.000 USD     0 trades
        2021-04-10  0.00000000 USDT  0.000 USD     0 trades
        2021-04-09  0.00000000 USDT  0.000 USD     0 trades
        2021-04-08  0.00000000 USDT  0.000 USD     0 trades
        2021-04-07  0.00000000 USDT  0.000 USD     0 trades
        2021-04-06  0.00000000 USDT  0.000 USD     0 trades
        """
        self.send_message("/daily not implemented yet")

    def _balance(self, update, context) -> None:
        """
        SXP:
            Available:  0.00136500
            Balance:  0.00136500
            Pending:  0.00000000
            Est. USDT:  0.00409227
        DOT:
            Available:  0.00974000
            Balance:  0.00974000
            Pending:  0.00000000
            Est. USDT:  0.37051739

        Estimated Value:
            USDT:  919.99068188
            USD:  919.99
        """
        self.send_message("/balance not implemented yet")

    def _forcesell(self, update, context) -> None:
        self.send_message("/forcesell not implemented yet")

    def clean(self) -> None:
        self._updater.stop()

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