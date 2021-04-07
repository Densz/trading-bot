import asyncio
import sys

from tradingbot.telegram import Telegram
from tradingbot.config import get_config
from tradingbot.database import Database
from tradingbot.worker import Worker
from tradingbot.exchange import Exchange
from tradingbot.exchange.exchange_resolver import ExchangeResolver

from strategies.main import Strategy


def main() -> None:
    config = get_config()
    database = Database(config, Strategy)
    exchange = ExchangeResolver.load_exchange(
        config["exchange"], config, database, Strategy
    )
    telegram = Telegram(config)
    worker = Worker(config, exchange, database, telegram)

    try:
        mode = "PAPER MODE" if config["paper_mode"] else "LIVE MODE"
        print(f"\033[36m==== 🚀 Starting trading bot ({mode}) 🚀 ====\033[39m")
        worker.start()
    except ValueError:
        print("Oops! An error occured")
    finally:
        asyncio.get_event_loop().run_until_complete(exchange.close_connection())
        telegram.clean()
        print(f"\033[36m==== ⛔ Stop trading bot ({mode}) ⛔ ====\033[39m")


if __name__ == "__main__":
    main()
