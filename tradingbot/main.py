import asyncio
from tradingbot.config import get_config
from tradingbot.database import Database
from tradingbot.worker import Worker
from tradingbot.exchange import Exchange
from tradingbot.exchange.exchange_resolver import ExchangeResolver

from strategies.main import Strategy


def main() -> None:
    config = get_config()
    mode = "PAPER MODE" if config['paper_mode'] else "LIVE MODE"
    print(
        f"\033[36m==== 🚀 Starting trading bot ({mode}) 🚀 ====\033[39m")
    database = Database(config, Strategy)
    exchange = ExchangeResolver.load_exchange(
        config['exchange'],
        config,
        database,
        Strategy
    )
    worker = Worker(config, exchange, database)

    try:
        worker.start()
    except ValueError:
        print("Oops! An error occured")
    finally:
        asyncio.get_event_loop().run_until_complete(exchange.close_connection())
        print(
            f"\033[36m==== ⛔ Stop trading bot ({mode}) ⛔ ====\033[39m")


if __name__ == '__main__':
    main()
