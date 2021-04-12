import asyncio
from tradingbot.exchange.binance import Binance
from typing import Optional

from tradingbot.telegram import Telegram
from tradingbot.config import get_config
from tradingbot.database import Database
from tradingbot.worker import Worker
from tradingbot.exchange.exchange_resolver import ExchangeResolver

from strategies.main import Strategy


class Bot:
    def __init__(self):
        self.config = get_config()
        self.strategy: Strategy = Strategy
        self.database: Database = Database(self)
        self.exchange: Binance = ExchangeResolver.load_exchange(self)
        self.telegram: Telegram = Telegram(self)

    def run(self):
        worker = Worker(self)

        mode = "PAPER MODE" if self.config["paper_mode"] else "LIVE MODE"
        print(f"\033[36m==== 🚀 Starting trading bot ({mode}) 🚀 ====\033[39m")

        worker.start()

    def clean(self):
        asyncio.get_event_loop().run_until_complete(self.exchange.close_connection())
        self.telegram.send_message("⛔ Stop trading bot ⛔")
        self.telegram.clean()
        print(f"\033[36m==== ⛔ Stop trading bot ⛔ ====\033[39m")

    def notify_buy(
        self,
        exchange: str,
        symbol: str,
        amount: float,
        open_rate: float,
        stop_loss: Optional[float] = 0,
        take_profit: Optional[float] = None,
    ):
        total_invested = amount * open_rate
        template = [
            [f"🔵 {exchange.title()}", f"Buying {symbol}\n"],
            ["Amount", f"{amount}\n"],
            ["Open rate", f"{open_rate}\n"],
            ["Total", f"{total_invested:.2f} USDT\n"],
            ["Stop loss price", f"{stop_loss}\n"],
            ["Take profit price", f"{take_profit if take_profit != None else ''}"],
        ]
        msg = self.format_array_to_msg(template)
        self.telegram.send_message(msg)

    def notify_sell(
        self,
        exchange: str,
        symbol: str,
        amount: float,
        open_rate: float,
        current_rate: float,
        close_rate: float,
        reason: str,
        profit: float = 0,
        profit_pct: float = 0,
    ):
        template = [
            [f"❌ {exchange.title()}", f"Selling {symbol}\n"],
            ["Amount", f"{amount}\n"],
            ["Open rate", f"{open_rate}\n"],
            ["Current rate", f"{current_rate}\n"],
            ["Close rate", f"{close_rate}\n"],
            ["Reason", f"{reason}\n"],
            ["Profit (%)", f"{profit_pct:.2f}%\n"],
            ["Profit (USDT)", f"{profit:.2f} USDT"],
        ]
        msg = self.format_array_to_msg(template)
        self.telegram.send_message(msg)

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
