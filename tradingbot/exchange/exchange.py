from strategies.main import Strategy


class Exchange:
    def __init__(self, config, database, strategy: Strategy) -> None:
        self._columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        self._db = database
        self._config = config
        self._strategy = strategy
