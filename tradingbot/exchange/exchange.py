import pandas as pd
from typing import Optional


class Exchange:
    def __init__(self, config, database) -> None:
        self._columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        self._db = database
        self._config = config
