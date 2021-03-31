from pprint import pprint
from typing import Optional
import ccxt.async_support as ccxt
import pandas as pd
import asyncio
from datetime import datetime

from tradingbot.exchange.exchange import Exchange
from tradingbot.database import Database, Trade
from strategies.main import Strategy


class Binance(Exchange):
    def __init__(self, config, database: Database, strategy: Strategy) -> None:
        Exchange.__init__(self, config, database, strategy)

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
        price: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        is_long=True,
    ):
        if (amount * price < 10):
            print('Could not create order less than 10 USDT')
            return
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
                amount_start=formatted_amount,
                amount_available=order['remaining'] if order != None else (
                    amount * (1 - trading_fee_rate)),
                open_order_id=order['id'] if order != None else "backtesting",
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
                take_profit=take_profit
            )
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
        else:
            try:
                trading_fee_rate = self.get_trading_fees()
                formatted_amount = self._api.amount_to_precision(
                    symbol, trade[0].amount_available)
                formatted_price = self._api.price_to_precision(symbol, price)
                order = None
                if (self._config['paper_mode'] == False):
                    order = await self._api.create_limit_sell_order(
                        symbol, formatted_amount, formatted_price, params=self._params)
                pprint(order)
                trade[0].update(
                    close_order_id=order['id'] if order != None else "backtesting",
                    close_order_status=order['status'] if order != None else "closed",
                    close_price_requested=formatted_price,
                    close_price=(order['price'] * (1 - trading_fee_rate)) if order != None else (float(formatted_price) * (
                        1 - trading_fee_rate)),
                    close_fee_rate=trading_fee_rate,
                    close_fee=(order['price'] * trading_fee_rate) if order != None else float(
                        formatted_price) * trading_fee_rate,
                    close_date=datetime.now(),
                    sell_reason=reason
                ).execute()
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

    async def trigger_stoploss_takeprofit(self):
        print("Trigger stoploss and takeprofit if there is")
        pass

    # ✅
    async def check_pending_orders(self):
        try:
            # Check open_order_status orders
            data = Trade.select().where(Trade.open_order_status == 'open').execute()
            for row in data:
                order_detail = await self._api.fetch_order(id=row.open_order_id, symbol=row.symbol)
                pprint(order_detail)
                if (order_detail['status'] != 'open'):
                    row.update(open_order_status=order_detail['status'],
                               open_cost=order_detail['cost']
                               ).execute()

            # Check close_order_status orders
            data = Trade.select().where(Trade.close_order_status == 'open').execute()
            for row in data:
                order_detail = await self._api.fetch_order(id=row.close_order_id, symbol=row.symbol)
                if (order_detail['status'] != 'open'):
                    profit = 0
                    profit_pct = 0
                    if (row.is_long == True):
                        profit = order_detail['cost'] - row.open_cost
                        profit_pct = (order_detail['cost'] / row.open_cost) - 1
                    else:
                        profit = row.open_cost - order_detail['cost']
                        profit_pct = (row.open_cost / order_detail['cost']) - 1

                    row.update(close_order_status=order_detail['status'],
                               close_cost=order_detail['cost'],
                               profit=profit,
                               profit_pct=profit_pct,
                               ).execute()
            return True
        except Exception as e:
            print('check_pending_orders() failed')
            print(e)
            return False
