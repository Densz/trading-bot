from os import close
from pprint import pprint
from typing import Optional
import ccxt.async_support as ccxt
import pandas as pd
import asyncio
from datetime import datetime
import uuid

from tradingbot.exchange.exchange import Exchange
from tradingbot.database import Database, Trade


class Binance(Exchange):
    def __init__(self, config, database: Database, strategy) -> None:
        Exchange.__init__(self, config, database, strategy)

        self._exchange_name = 'binance'

        self._api: ccxt.binance = ccxt.binance({**config['binance']})
        asyncio.get_event_loop().run_until_complete(self._api.load_markets())
        # ccxt params for making calls
        self._params = {'test': config['paper_mode']}

    # ✅
    async def fetch_current_ohlcv(self, tick: str):
        # print(self._api.iso8601(self._api.milliseconds()),
        #       'fetching', tick, 'ticker from', self._api.name)
        tick_info = await self._api.fetch_ticker(tick)
        current_tick: Tick = {
            'symbol': tick_info['symbol'],
            'high': tick_info['high'],
            'low': tick_info['low'],
            'open': tick_info['open'],
            'close': tick_info['close'],
            'baseVolume': tick_info['baseVolume'],
        }
        return current_tick

    # ✅
    async def fetch_historic_ohlcv(self, tickers, timeframe) -> pd.DataFrame:
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
        price: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        is_long=True,
    ):
        open_trade = self._db.has_trade_open(symbol=symbol)
        if (open_trade != None):
            print(
                '\033[31mCould not create order, a trade already exists and is not closed yet\033[39m')
            return False

        if (amount * price < 10):
            print('\033[31mCould not create order less than 10 USDT\033[39m')
            return False
        try:
            trading_fee_rate = self.get_trading_fees()
            formatted_amount = self._api.amount_to_precision(symbol, amount)
            formatted_price = self._api.price_to_precision(symbol, price)
            order = None
            if (self._config['paper_mode'] == False):
                order = await self._api.create_limit_buy_order(
                    symbol, formatted_amount, formatted_price, params=self._params)
            Trade.create(
                exchange=self._exchange_name,
                symbol=symbol,
                strategy=self._strategy.strategy_params['id'],
                timeframe=self._strategy.timeframe,
                is_long=is_long,
                amount=formatted_amount,
                open_order_id=order['id'] if order != None else uuid.uuid4(),
                open_order_status=order['status'] if order != None else "closed",
                open_price_requested=formatted_price,
                open_price=(order['price'] * (1 - trading_fee_rate)) if order != None else (float(formatted_price) * (
                    1 - trading_fee_rate)),
                open_fee_rate=trading_fee_rate,
                open_fee=(order['price'] * trading_fee_rate) if order != None else float(
                    formatted_price) * trading_fee_rate,
                open_date=datetime.now(),
                initial_stop_loss=stop_loss,
                current_stop_loss=stop_loss,
                take_profit=take_profit,
                open_cost=amount * price if order == None else None
            )
            print(
                f"\033[32mCREATE BUY ORDER: Symbol: [{symbol}], Asked price [{formatted_price}], Asked amount [{formatted_amount}]\033[39m")
        except ccxt.InsufficientFunds as e:
            print('create_buy_order() failed – not enough funds')
            print(e)
            return False
        except Exception as e:
            print('create_buy_order() failed')
            print(e)
            return False
        return True

    # ✅
    async def create_sell_order(self, symbol: str, price: float, trade_id: Optional[int] = None, reason: str = ''):
        trade = None
        if (trade_id):
            trade = Trade.select().where(Trade.symbol == symbol,
                                         Trade.id == trade_id,
                                         Trade.close_order_id == None).execute()
        else:
            trade = Trade.select().where(Trade.symbol == symbol,
                                         Trade.close_order_id == None).execute()
        if (len(trade) != 1):
            print(
                "\033[31mError: Could not create sell order because zero or more than one trade found in db \033[39m")
            return False
        if (trade[0].open_order_status == 'open'):
            print(
                "\033[31mError: Could not create sell order because open order has not been filled \033[39m")
            return False
        try:
            trading_fee_rate = self.get_trading_fees()
            formatted_amount = self._api.amount_to_precision(
                symbol, trade[0].amount)
            formatted_price = self._api.price_to_precision(symbol, price)
            close_cost = float(formatted_amount) * float(formatted_price)
            profit = 0
            profit_pct = 0
            if (trade[0].is_long == True):
                profit = close_cost - trade[0].open_cost
                profit_pct = (close_cost / trade[0].open_cost) - 1
            else:
                profit = trade[0].open_cost - close_cost
                profit_pct = (trade[0].open_cost / close_cost) - 1

            order = None
            if (self._config['paper_mode'] == False):
                order = await self._api.create_limit_sell_order(
                    symbol, formatted_amount, formatted_price, params=self._params)

            Trade.update(
                close_order_id=order['id'] if order != None else uuid.uuid4(),
                close_order_status=order['status'] if order != None else "closed",
                close_price_requested=formatted_price,
                close_price=(order['price'] * (1 - trading_fee_rate)) if order != None else (float(formatted_price) * (
                    1 - trading_fee_rate)),
                close_fee_rate=trading_fee_rate,
                close_fee=(order['price'] * trading_fee_rate) if order != None else float(
                    formatted_price) * trading_fee_rate,
                close_date=datetime.now(),
                sell_reason=reason,
                close_cost=close_cost if order == None else None,
                profit=profit if order == None else None,
                profit_pct=profit_pct if order == None else None,
            ).where(Trade.open_order_id == trade[0].open_order_id).execute()
            print(
                f"\033[31mCREATE SELL ORDER: Symbol: [{symbol}], Asked price [{formatted_price}], Asked amount [{formatted_amount}], Reason: [{reason}], Profit: [${profit:.2f}], Profit %: [{profit_pct:.3f}%]\033[39m")
        except ccxt.InsufficientFunds as e:
            print('create_sell_order() failed – not enough funds')
            print(e)
            return False
        except Exception as e:
            print('create_sell_order() failed')
            print(e)
            return False
        return True

    # ✅
    def get_trading_fees(self):
        return 0.001

    # ✅
    def get_market_symbols(self):
        return self._api.symbols

    # ✅
    async def close_connection(self):
        await self._api.close()

    async def trigger_stoploss_takeprofit(self, symbol, ohlc) -> None:
        open_orders = self._db.get_open_orders(symbol=symbol)

        if (open_orders == None):
            return
        # print("Open orders ===>")
        for order in open_orders:
            # All fields in db
            # pprint(dir(order))
            """
            {'baseVolume': 2020700362.0,
            'close': 0.0582203,
            'high': 0.0592851,
            'low': 0.0561885,
            'open': 0.0564656,
            'symbol': 'DOGE/USDT'}
            """
            pprint(ohlc)

        pass

    # ✅
    async def check_pending_orders(self) -> None:
        if (self._config['paper_mode'] == True):
            return
        try:
            # Check open_order_status orders
            data = Trade.select().where(Trade.open_order_status == 'open').execute()
            for row in data:
                order_detail = await self._api.fetch_order(id=row.open_order_id, symbol=row.symbol)
                if (order_detail['status'] == 'closed'):
                    Trade.update(open_order_status=order_detail['status'],
                                 open_cost=order_detail['cost'],
                                 ).where(Trade.open_order_id == row.open_order_id).execute()
        except Exception as e:
            print('check_pending_orders() for buy orders failed')
            print(e)

        try:
            # Check close_order_status orders
            data = Trade.select().where(Trade.close_order_status == 'open').execute()
            for row in data:
                order_detail = await self._api.fetch_order(id=row.close_order_id, symbol=row.symbol)
                if (order_detail['status'] == 'closed'):
                    profit = 0
                    profit_pct = 0
                    if (row.is_long == True):
                        profit = order_detail['cost'] - row.open_cost
                        profit_pct = (order_detail['cost'] / row.open_cost) - 1
                    else:
                        profit = row.open_cost - order_detail['cost']
                        profit_pct = (row.open_cost / order_detail['cost']) - 1
                    Trade.update(close_order_status=order_detail['status'],
                                 close_cost=order_detail['cost'],
                                 profit=profit,
                                 profit_pct=profit_pct,
                                 ).where(Trade.open_order_id == row.open_order_id).execute()
        except Exception as e:
            print('check_pending_orders() for sell orders failed')
            print(e)
