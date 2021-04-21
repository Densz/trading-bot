import asyncio
import importlib
from tradingbot.exchange.binance import Binance

from tradingbot.telegram import Telegram
from tradingbot.config import get_config
from tradingbot.database import Database
from tradingbot.worker import Worker
from tradingbot.exchange.exchange_resolver import ExchangeResolver


class Bot:
    def __init__(self):
        self.config = get_config()
        self.strategy = self.get_strategy_from_name(self.config["strategy"])

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

    @staticmethod
    def get_strategy_from_name(strategy: str):
        try:
            StrategyClass = getattr(
                importlib.import_module(f"strategies.{strategy}"),
                "Strategy",
            )
            return StrategyClass
        except:
            print(
                f"Could not find strategy [{strategy}.py], please change your config.json file. Please also make sure that the class of the file is named [class Strategy]"
            )