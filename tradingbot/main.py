from tradingbot.exchange import Exchange
from tradingbot.config import get_config
from strategies.main import Strategy


def main() -> None:
    print("==== 🚀 Starting trading bot 🚀 ====")

    config = get_config()

    exchange = Exchange(config)

    print(Strategy.startup_candles)
    print(Strategy.tickers)


if __name__ == '__main__':
    main()
