from tradingbot.trade import Trade
from tradingbot.worker import Worker

from tradingbot.exchange import Exchange
from tradingbot.config import get_config
from strategies.main import Strategy


def main() -> None:
    print("==== 🚀 Starting trading bot 🚀 ====")
    config = get_config()
    exchange = Exchange(config)
    trade = Trade(config)
    worker = Worker(config, exchange, trade)

    try:
        worker.start()
    except ValueError:
        print("Oops! An error occured")
    finally:
        print("==== 🚀 Stop trading bot 🚀 ====")


if __name__ == '__main__':
    main()
