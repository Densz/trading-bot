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
    def __init__(self, config, database) -> None:
        self._api: ccxt.Exchange = ccxt.binance({
            **config['binance']
        })
        self._api.load_markets()
        self._api_async: ccxt_async.Exchange = ccxt_async.binance()
        self._db = database
        self._params = {
            'test': config['dry_run']
        }

    # ✅
    def fetch_ticker(self, tick: str):
        return self._api.fetch_ticker(tick)

    # ✅
    def fetch_ohlcv(self, tickers, timeframe) -> pd.DataFrame:
        data: list = self._api.fetch_ohlcv(tickers, timeframe)
        df = pd.DataFrame(data, columns=DEFAULT_DATAFRAME_COLUMNS)
        df['date'] = pd.to_datetime(df['date'], unit='ms')
        return df

    # ✅
    def get_balance(self, currency):
        balances = self._api.fetch_total_balance()
        return balances[currency]

    # ✅
    def get_market_symbols(self):
        return self._api.symbols

    # ✅
    def create_buy_order(
        self, symbol: str,
        amount: float,
        price: Optional[float] = None,
        stop_loss: Optional[float] = None
    ):
        if (amount * price < 10):
            return 'Could not create order less than 10 USDT'
        """
        {
            'amount': 400.0,
            'average': None,
            'clientOrderId': 'x-R4BD3S82c5dc5801380c7e2c35f7cd',
            'cost': 0.0,
            'datetime': '2021-03-25T11:23:37.010Z',
            'fee': None,
            'filled': 0.0,
            'id': '409646107',
            'info': {'clientOrderId': 'x-R4BD3S82c5dc5801380c7e2c35f7cd',
                    'cummulativeQuoteQty': '0.00000000',
                    'executedQty': '0.00000000',
                    'orderId': 409646107,
                    'orderListId': -1,
                    'origQty': '400.00000000',
                    'price': '0.03233600',
                    'side': 'BUY',
                    'status': 'NEW',
                    'symbol': 'DOGEUSDT',
                    'timeInForce': 'GTC',
                    'transactTime': 1616671417010,
                    'type': 'LIMIT'},
            'lastTradeTimestamp': None,
            'postOnly': False,
            'price': 0.032336,
            'remaining': 400.0,
            'side': 'buy',
            'status': 'open',
            'stopPrice': None,
            'symbol': 'DOGE/USDT',
            'timeInForce': 'GTC',
            'timestamp': 1616671417010,
            'trades': None,
            'type': 'limit'
        }
        """
        return self._api.create_limit_buy_order(
            symbol, amount, price, params=self._params)

    def update_order(self, order_id, stop_loss: None, take_profit: None):
        print("update_order")

    def create_sell_order(self, order_id, at_price):
        print("sell_order")

    def cancel_order(self, order_id):
        print("cancel_order")

    def get_trading_fees(self):
        return 0.001

# sell one ฿ for market price and receive $ right now
# print(binance.id, binance.create_market_sell_order('BTC/USD', 1))

# limit buy BTC/EUR, you pay €2500 and receive ฿1  when the order is closed
# print(exmo.id, exmo.create_limit_buy_order('BTC/EUR', 1, 2500.00))

# pass/redefine custom exchange-specific order params: type, amount, price, flags, etc...
# kraken.create_market_buy_order('BTC/USD', 1, {'trading_agreement': 'agree'})
