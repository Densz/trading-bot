import ccxt.async_support as ccxt
import pandas as pd
import asyncio
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
        asyncio.get_event_loop().run_until_complete(self._api.load_markets())
        self._db = database
        self._params = {
            'test': config['dry_run']
        }

    # ✅
    async def fetch_ticker(self, tick: str):
        # print(self._api.iso8601(self._api.milliseconds()),
        #       'fetching', tick, 'ticker from', self._api.name)
        return await self._api.fetch_ticker(tick)

    # ✅
    async def fetch_ohlcv(self, tickers, timeframe) -> pd.DataFrame:
        data: list = await self._api.fetch_ohlcv(tickers, timeframe)
        df = pd.DataFrame(data, columns=DEFAULT_DATAFRAME_COLUMNS)
        df['date'] = pd.to_datetime(df['date'], unit='ms')
        return df

    # ✅
    async def get_balance(self, currency):
        balances = await self._api.fetch_total_balance()
        return balances[currency]

    # ✅
    async def create_buy_order(
        self, symbol: str,
        amount: float,
        price: Optional[float] = None,
        stop_loss: Optional[float] = None
    ):
        if (amount * price < 10):
            print('Could not create order less than 10 USDT')
            return
        try:
            formatted_amount = self._api.amount_to_precision(symbol, amount)
            print('Amount: ', str(amount))
            print('Formatted amount: ', str(formatted_amount))
            formatted_price = self._api.price_to_precision(symbol, price)
            print('Price: ', str(price))
            print('Formatted price: ', str(formatted_price))
            order = await self._api.create_limit_buy_order(
                symbol, formatted_amount, formatted_price, params=self._params)
            pprint(order)
        except ccxt.InsufficientFunds as e:
            print('create_order() failed – not enough funds')
            print(e)
        except Exception as e:
            print('create_order() failed')
            print(e)
        return

    # def get_trades(self):

    def update_order(self, order_id, stop_loss: None, take_profit: None):
        print("update_order")

    def create_sell_order(self, order_id, at_price):
        print("sell_order")

    def cancel_order(self, order_id):
        print("cancel_order")

    def get_trading_fees(self):
        return 0.001

    # ✅
    def get_market_symbols(self):
        return self._api.symbols

    async def close_connection(self):
        await self._api.close()
