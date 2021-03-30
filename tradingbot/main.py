import asyncio
from tradingbot.config import get_config
from tradingbot.database import Database
from tradingbot.worker import Worker
from tradingbot.exchange import Exchange
from tradingbot.exchange.exchange_resolver import ExchangeResolver

from strategies.main import Strategy


def main() -> None:
    print("==== 🚀 Starting trading bot 🚀 ====")
    config = get_config()
    database = Database(config)
    exchange = ExchangeResolver.load_exchange(
        config['exchange'],
        config,
        database
    )
    worker = Worker(config, exchange)

    try:
        worker.start()
    except ValueError:
        print("Oops! An error occured")
    finally:
        asyncio.get_event_loop().run_until_complete(exchange.close_connection())
        print("==== 🚀 Stop trading bot 🚀 ====")


if __name__ == '__main__':
    main()
