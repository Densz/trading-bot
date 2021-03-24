import ccxt.async_support as ccxt
import ccxt
import pandas as pd
import ccxt.async_support as ccxt_async
from ccxt.base.decimal_to_precision import (ROUND_DOWN, ROUND_UP, TICK_SIZE, TRUNCATE,
                                            decimal_to_precision)
from typing import Dict, Optional
from pprint import pprint

from datetime import datetime


DEFAULT_DATAFRAME_COLUMNS = ['date', 'open', 'high', 'low', 'close', 'volume']


class Exchange:
    def __init__(self, config) -> None:
        self._api: ccxt.Exchange = ccxt.binance({
            **config['binance']
        })
        self._api.load_markets()
        self._api_async: ccxt_async.Exchange = None

    def fetch_tickers(self, tickers):
        return self._api.fetch_tickers(tickers)

    def fetch_ohlcv(self, tickers, timeframe) -> pd.DataFrame:
        data: list = self._api.fetch_ohlcv(tickers, timeframe)
        df = pd.DataFrame(data, columns=DEFAULT_DATAFRAME_COLUMNS)
        df['date'] = pd.to_datetime(df['date'], unit='ms')
        return df

    def get_balance(self, currency):
        balances = self._api.fetch_total_balance()
        return balances[currency]

    def get_market_symbols(self):
        return self._api.symbols

    def create_buy_order(self, stop_loss, at_price):
        print("place_order")

    def update_order(self, order_id, stop_loss: None, take_profit: None):
        print("update_order")

    def create_sell_order(self, order_id, at_price):
        print("sell_order")

    def cancel_order(self, order_id):
        print("cancel_order")

    def get_trading_fees(self):
        return 0.001

# ohlcv = self._api.fetch_ohlcv('BTC/USDT', '1h', since='20200101')
# print(ohlcv)
# return self._api.calculate_fee()

# market = binance.load_markets()
# binance_available_symbols = binance.symbols
# print(binance_available_symbols.index('BTC/USDT'))
# print(binance.fetch_order_book(binance.symbols[0]))
# print(binance.fetch_ticker('BTC/USD'))
# print(binance.fetch_trades('LTC/USDT'))

# print(binance.fetch_balance())

# sell one ฿ for market price and receive $ right now
# print(binance.id, binance.create_market_sell_order('BTC/USD', 1))

# limit buy BTC/EUR, you pay €2500 and receive ฿1  when the order is closed
# print(exmo.id, exmo.create_limit_buy_order('BTC/EUR', 1, 2500.00))

# pass/redefine custom exchange-specific order params: type, amount, price, flags, etc...
# kraken.create_market_buy_order('BTC/USD', 1, {'trading_agreement': 'agree'})
