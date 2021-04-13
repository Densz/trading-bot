from tradingbot.database import Database
import tradingbot.exchange as Exchanges

AVAILABLE_EXCHANGE = ["binance", "oanda"]


class ExchangeResolver:
    @staticmethod
    def load_exchange(bot):
        exchange = None

        AVAILABLE_EXCHANGE.index(bot.config["exchange"])
        exchange_class = getattr(Exchanges, bot.config["exchange"].title())

        exchange = exchange_class(bot)

        return exchange
