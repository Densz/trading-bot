class Exchange:
    def __init__(self, config, database, strategy) -> None:
        self._columns = ["date", "open", "high", "low", "close", "volume"]
        self._db = database
        self._config = config
        self._strategy = strategy
