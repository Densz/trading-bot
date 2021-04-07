from strategies.main import Strategy
from tradingbot.database import Database
import tradingbot.exchange as Exchanges

AVAILABLE_EXCHANGE = ["binance", "oanda"]


class ExchangeResolver:
    @staticmethod
    def load_exchange(
        exchange_name: str, config, database: Database, strategy: Strategy
    ):
        exchange = None

        AVAILABLE_EXCHANGE.index(exchange_name)
        exchange_class = getattr(Exchanges, exchange_name.title())

        exchange = exchange_class(config, database, strategy)

        return exchange
