from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tradingbot.bot import Bot


class Exchange:
    def __init__(self, bot) -> None:
        self._columns = ["date", "open", "high", "low", "close", "volume"]
        self.bot: Bot = bot
