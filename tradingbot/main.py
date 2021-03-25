from tradingbot.config import get_config
from tradingbot.database import Database
from tradingbot.worker import Worker
from tradingbot.exchange import Exchange
from strategies.main import Strategy


def main() -> None:
    print("==== 🚀 Starting trading bot 🚀 ====")
    config = get_config()
    database = Database(config)
    exchange = Exchange(config, database)
    worker = Worker(config, exchange)

    try:
        worker.start()
    except ValueError:
        print("Oops! An error occured")
    finally:
        print("==== 🚀 Stop trading bot 🚀 ====")


if __name__ == '__main__':
    main()
