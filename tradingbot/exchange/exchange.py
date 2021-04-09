class Exchange:
    def __init__(self, bot) -> None:
        self._columns = ["date", "open", "high", "low", "close", "volume"]
        self.bot = bot
