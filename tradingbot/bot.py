import importlib
import sys
from tradingbot.strategy import IStrategy
from tradingbot.exchange import Exchange

from tradingbot.chat import Telegram
from tradingbot.config import get_config
from tradingbot.database import Database
from tradingbot.worker import Worker
from tradingbot.exchange.exchange_resolver import ExchangeResolver


class Bot:
    def __init__(self) -> None:
        self.config = get_config()
        self.strategy: IStrategy = self.get_strategy_from_name(self.config["strategy"])

        self.database: Database = Database(self)
        self.exchange: Exchange = ExchangeResolver.load_exchange(self)
        self.telegram: Telegram = Telegram(self)

    def run(self) -> None:
        worker = Worker(self)

        mode = "PAPER MODE" if self.config["paper_mode"] else "LIVE MODE"
        print(f"\033[36m==== 🚀 Starting trading bot ({mode}) 🚀 ====\033[39m")

        worker.start()

    def clean(self) -> None:
        msg = "⛔ Stop trading bot ⛔"
        self.telegram.send_message(msg)
        self.telegram.clean()
        print(f"\033[36m==== {msg} ====\033[39m")

    @staticmethod
    def get_strategy_from_name(strategy: str) -> IStrategy:
        try:
            StrategyClass = getattr(
                importlib.import_module(f"strategies.{strategy}"),
                "Strategy",
            )
            return StrategyClass
        except:
            print("ERROR: An error occured: " + str(sys.exc_info()[0]))
            raise BaseException(
                f"ERROR: Could not find strategy [{strategy}.py], please change your config.json file. Please also make sure that the class of the file is named [class Strategy]"
            )