from typing import Optional
import ccxt.async_support as ccxt
import pandas as pd
import asyncio

from tradingbot.exchange.exchange import Exchange
from tradingbot.database import Trade


class Binance(Exchange):
    def __init__(self, config, database) -> None:
        Exchange.__init__(self, config, database)

        self._exchange_name = 'binance'

        self._api: ccxt.Exchange = ccxt.binance({**config['binance']})
        asyncio.get_event_loop().run_until_complete(self._api.load_markets())
        # ccxt params for making calls
        self._params = {'test': config['paper_mode']}

    # ✅
    async def fetch_symbol(self, tick: str):
        # print(self._api.iso8601(self._api.milliseconds()),
        #       'fetching', tick, 'ticker from', self._api.name)
        return await self._api.fetch_ticker(tick)

    # ✅
    async def fetch_ohlcv(self, tickers, timeframe) -> pd.DataFrame:
        data: list = await self._api.fetch_ohlcv(tickers, timeframe)
        df = pd.DataFrame(data, columns=self._columns)
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
            formatted_price = self._api.price_to_precision(symbol, price)
            if (self._config['paper_mode'] == False):
                # order = await self._api.create_limit_buy_order(
                #     symbol, formatted_amount, formatted_price, params=self._params)
                # pprint(order)
                Trade.create()
            else:
                Trade.create()
        except ccxt.InsufficientFunds as e:
            print('create_order() failed – not enough funds')
            print(e)
        except Exception as e:
            print('create_order() failed')
            print(e)
        return

    def update_order(self, order_id, stop_loss: None, take_profit: None):
        print("update_order")

    def create_sell_order(self, order_id, at_price):
        print("sell_order")

    def get_trading_fees(self):
        return 0.001

    # ✅
    def get_market_symbols(self):
        return self._api.symbols

    # ✅
    async def close_connection(self):
        await self._api.close()
