import asyncio

from tradingbot.telegram import Telegram
from tradingbot.config import get_config
from tradingbot.database import Database
from tradingbot.worker import Worker
from tradingbot.exchange.exchange_resolver import ExchangeResolver

from strategies.main import Strategy


class Bot:
    def __init__(self):
        self.config = get_config()
        self.database = Database(self.config, Strategy)
        self.exchange = ExchangeResolver.load_exchange(
            exchange_name=self.config["exchange"],
            config=self.config,
            database=self.database,
            strategy=Strategy,
            bot=self,
        )
        self.telegram = Telegram(self.config, self.exchange)

    def run(self):
        worker = Worker(self.config, self.exchange, self.database, self.telegram)

        mode = "PAPER MODE" if self.config["paper_mode"] else "LIVE MODE"
        print(f"\033[36m==== 🚀 Starting trading bot ({mode}) 🚀 ====\033[39m")

        worker.start()

    def clean(self):
        asyncio.get_event_loop().run_until_complete(self.exchange.close_connection())
        self.telegram.clean()
        print(f"\033[36m==== ⛔ Stop trading bot ⛔ ====\033[39m")

    def send_msg(self, msg):
        self.telegram.send_message(msg)


def main() -> None:
    try:
        bot = Bot()
        bot.run()
    except ValueError:
        print("Oops! An error occured")
    except KeyboardInterrupt:
        print("SIGINT received, aborting ...")
    finally:
        if bot:
            bot.clean()


if __name__ == "__main__":
    main()
