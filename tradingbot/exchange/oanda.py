from tradingbot.exchange import Exchange


class Oanda(Exchange):
    def __init__(self, bot) -> None:
        self.bot = bot
        self._api: None
