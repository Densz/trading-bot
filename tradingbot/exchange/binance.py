from tradingbot.types import Tick
from typing import Optional
import ccxt
import ccxt.async_support as ccxt_async
import pandas as pd
import asyncio
from datetime import datetime
import uuid

from tradingbot.exchange.exchange import Exchange
from tradingbot.database import Trade

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tradingbot.bot import Bot


class Binance(Exchange):
    def __init__(self, bot: "Bot") -> None:
        Exchange.__init__(self, bot)
        self._api: ccxt.binance = ccxt.binance({**self.bot.config["binance"]})
        self._api_async: ccxt_async.binance = ccxt_async.binance(
            {**self.bot.config["binance"]}
        )
        # ccxt params for making calls
        self._params = {"test": self.bot.config["paper_mode"]}
        self._api.load_markets()
        asyncio.get_event_loop().run_until_complete(self._api_async.load_markets())

    async def fetch_current_ohlcv(self, tick: str) -> Tick:
        tick_info = await self._api_async.fetch_ticker(tick)
        current_tick: Tick = {
            "symbol": tick_info["symbol"],
            "high": tick_info["high"],
            "low": tick_info["low"],
            "open": tick_info["open"],
            "close": tick_info["close"],
            "baseVolume": tick_info["baseVolume"],
        }
        return current_tick

    async def fetch_historic_ohlcv(self, tickers, timeframe) -> pd.DataFrame:
        data: list = await self._api_async.fetch_ohlcv(tickers, timeframe)
        df = pd.DataFrame(data, columns=self._columns)
        df["date"] = pd.to_datetime(df["date"], unit="ms")
        return df

    # Get balance available in the main currency on Binance
    # Example response: 945.123 (of the main currency)
    def get_balance(self, symbol) -> float:
        balances = self._api.fetch_total_balance()
        return balances[symbol]

    # Return the last close price of the tickers in the array
    # Example response: {
    #   "DOGE/USDT": 0.09213,
    #   "BTC/USDT": 0.12312
    # }
    def get_tickers(self, symbols) -> float:
        try:
            ticks = self._api.fetch_tickers(symbols)
            result = {}
            for key in ticks:
                result[key] = ticks[key]["last"]
            return result
        except ValueError as e:
            print("Fail getting sell value (ask price)", e)
            return None

    def get_tradable_balance(self) -> float:
        open_orders_allocated_amount = self.bot.database.get_used_amount()
        amount_allocated_to_strat = self.bot.strategy.amount_allocated

        if self.bot.config["paper_mode"] == True:
            return amount_allocated_to_strat - open_orders_allocated_amount

        balance_available_in_broker = self.get_balance(self.bot.strategy.main_currency)

        if amount_allocated_to_strat >= balance_available_in_broker:
            return balance_available_in_broker - open_orders_allocated_amount

        return amount_allocated_to_strat - open_orders_allocated_amount

    def create_buy_order(
        self,
        symbol: str,
        amount: float,
        price: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        is_long=True,
    ):
        open_trade = self.bot.database.has_trade_open(symbol=symbol)
        tradable_balance = self.get_tradable_balance()

        if open_trade != None:
            print(
                "\033[31mCould not create order, a trade already exists and is not closed yet\033[39m"
            )
            return False
        if amount * price > tradable_balance:
            print("\033[31mCould not create order insufficient funds\033[39m")
            return False
        if amount * price < 10:
            print("\033[31mCould not create order less than 10 USDT\033[39m")
            return False

        try:
            trading_fee_rate = self.get_trading_fees()
            formatted_amount = self._api_async.amount_to_precision(symbol, amount)
            formatted_price = self._api_async.price_to_precision(symbol, price)
            order = None
            if self.bot.config["paper_mode"] == False:
                order = self._api.create_limit_buy_order(
                    symbol, formatted_amount, formatted_price, params=self._params
                )
                Trade.create(
                    exchange=self.bot.config["exchange"],
                    symbol=symbol,
                    strategy=self.bot.strategy.strategy_params["id"],
                    timeframe=self.bot.strategy.timeframe,
                    is_long=is_long,
                    amount_requested=float(formatted_amount),
                    amount_available=((1 - trading_fee_rate) * float(formatted_amount)),
                    open_order_id=order["id"] if order != None else uuid.uuid4(),
                    open_order_status="open",
                    open_price_requested=float(formatted_price),
                    open_date=datetime.now(),
                    initial_stop_loss=stop_loss,
                    current_stop_loss=stop_loss,
                    take_profit=take_profit,
                )
            else:
                Trade.create(
                    exchange=self.bot.config["exchange"],
                    symbol=symbol,
                    strategy=self.bot.strategy.strategy_params["id"],
                    timeframe=self.bot.strategy.timeframe,
                    is_long=is_long,
                    amount_requested=float(formatted_amount),
                    amount_available=(1 - trading_fee_rate) * float(formatted_amount),
                    open_order_id=uuid.uuid4(),
                    open_order_status="closed",
                    open_price_requested=float(formatted_price),
                    open_price=float(formatted_price),
                    open_fee_rate=trading_fee_rate,
                    open_fee=trading_fee_rate
                    * float(formatted_amount)
                    * float(formatted_price),
                    open_cost=float(formatted_price) * float(formatted_amount),
                    open_date=datetime.now(),
                    initial_stop_loss=stop_loss,
                    current_stop_loss=stop_loss,
                    take_profit=take_profit,
                )
            self.bot.notify_buy(
                exchange=self.bot.config["exchange"],
                symbol=symbol,
                amount=float(formatted_amount),
                open_rate=float(formatted_price),
                stop_loss=stop_loss,
                take_profit=take_profit,
            )
        except ccxt.InsufficientFunds as e:
            print("create_buy_order() failed – not enough funds")
            print(e)
            return False
        except Exception as e:
            print("create_buy_order() failed")
            print(e)
            return False
        return True

    def create_sell_order(
        self,
        symbol: str,
        price: float,
        trade_id: Optional[int] = None,
        reason: str = "",
    ) -> bool:
        trade = None
        if trade_id:
            trade = (
                Trade.select()
                .where(
                    Trade.symbol == symbol,
                    Trade.id == trade_id,
                    Trade.close_order_id == None,
                )
                .execute()
            )
        else:
            trade = (
                Trade.select()
                .where(
                    Trade.strategy == self.bot.strategy.strategy_params["id"],
                    Trade.symbol == symbol,
                    Trade.close_order_id == None,
                )
                .execute()
            )
        if len(trade) != 1:
            print(
                "\033[31mError: Could not create sell order because zero or more than one trade found in db \033[39m"
            )
            return False
        if trade[0].open_order_status == "open":
            print(
                "\033[31mError: Could not create sell order because open order has not been filled \033[39m"
            )
            return False
        try:
            trading_fee_rate = self.get_trading_fees()
            formatted_amount = self._api.amount_to_precision(
                symbol, trade[0].amount_available
            )
            formatted_price = self._api.price_to_precision(symbol, price)
            order = None
            if self.bot.config["paper_mode"] == False:
                order = self._api.create_limit_sell_order(
                    symbol, formatted_amount, formatted_price, params=self._params
                )
                Trade.update(
                    close_order_id=order["id"] if order != None else uuid.uuid4(),
                    close_order_status="open",
                    close_price_requested=formatted_price,
                    close_date=datetime.now(),
                    sell_reason=reason,
                ).where(Trade.open_order_id == trade[0].open_order_id).execute()
            else:
                [profit, profit_pct, close_return] = self.calculate_profit(
                    open_cost=trade[0].open_cost,
                    amount_available=trade[0].amount_available,
                    close_price=price,
                    trading_fee_rate=trading_fee_rate,
                )
                Trade.update(
                    close_order_id=uuid.uuid4(),
                    close_order_status="closed",
                    close_price_requested=formatted_price,
                    close_price=float(formatted_price),
                    close_fee_rate=trading_fee_rate,
                    close_fee=(
                        trading_fee_rate
                        * float(trade[0].amount_available)
                        * float(formatted_price)
                    ),
                    close_return=close_return,
                    close_date=datetime.now(),
                    profit=profit,
                    profit_pct=profit_pct,
                    sell_reason=reason,
                ).where(Trade.open_order_id == trade[0].open_order_id).execute()
            self.bot.notify_sell(
                exchange=self.bot.config["exchange"],
                symbol=symbol,
                amount=trade[0].amount_requested,
                open_rate=trade[0].open_price,
                current_rate=price,
                close_rate=price,
                reason=reason,
                profit=profit,
                profit_pct=profit_pct * 100,
            )
        except ccxt.InsufficientFunds as e:
            print("create_sell_order() failed – not enough funds")
            print(e)
            return False
        except Exception as e:
            print("create_sell_order() failed")
            print(e)
            return False
        return True

    def get_trading_fees(self):
        return 0.001

    def get_market_symbols(self):
        return self._api_async.symbols

    async def close_connection(self):
        await self._api_async.close()

    async def trigger_stoploss_takeprofit(self, symbol, ohlc) -> None:
        open_orders = self.bot.database.get_open_orders(symbol=symbol)

        if open_orders == None:
            return
        for order in open_orders:
            if order.initial_stop_loss and ohlc["close"] <= order.initial_stop_loss:
                self.create_sell_order(
                    symbol=order.symbol,
                    price=ohlc["close"],
                    trade_id=order.id,
                    reason="Stoploss",
                )
                return
            if order.current_stop_loss and ohlc["close"] <= order.current_stop_loss:
                self.create_sell_order(
                    symbol=order.symbol,
                    price=ohlc["close"],
                    trade_id=order.id,
                    reason="Ajusted stoploss",
                )
                return
            if order.take_profit and ohlc["close"] >= order.take_profit:
                self.create_sell_order(
                    symbol=order.symbol,
                    price=ohlc["close"],
                    trade_id=order.id,
                    reason="Takeprofit",
                )
                return

    async def check_pending_orders(self) -> None:
        if self.bot.config["paper_mode"] == True:
            return

        trading_fee_rate = self.get_trading_fees()

        try:
            # Check open_order_status orders
            data = Trade.select().where(Trade.open_order_status == "open").execute()
            for row in data:
                order_detail = await self._api_async.fetch_order(
                    id=row.open_order_id, symbol=row.symbol
                )
                if order_detail["status"] == "closed":
                    Trade.update(
                        open_order_status=order_detail["status"],
                        open_cost=order_detail["cost"],
                        open_fee_rate=trading_fee_rate,
                        open_price=order_detail["average"],
                        open_fee=(
                            (trading_fee_rate * order_detail["amount"])
                            * order_detail["average"]
                        ),
                    ).where(Trade.open_order_id == row.open_order_id).execute()
                    print(
                        f"\033[32m ✅ EXECUTED BUY ORDER: Symbol: [{order_detail['symbol']}], Asked price [{order_detail['average']}], Asked amount [{order_detail['amount']}]\033[39m"
                    )
        except Exception as e:
            print("check_pending_orders() for buy orders failed")
            print(e)

        try:
            # Check close_order_status orders
            data = Trade.select().where(Trade.close_order_status == "open").execute()
            for row in data:
                order_detail = await self._api_async.fetch_order(
                    id=row.close_order_id, symbol=row.symbol
                )
                if order_detail["status"] == "closed":
                    [profit, profit_pct, close_return] = self.calculate_profit(
                        open_cost=order_detail["cost"],
                        amount_available=order_detail["amount_available"],
                        close_price=order_detail["average"],
                        trading_fee_rate=trading_fee_rate,
                    )
                    Trade.update(
                        close_order_status="closed",
                        close_price=order_detail["average"],
                        close_fee_rate=trading_fee_rate,
                        close_fee=order_detail["cost"] * trading_fee_rate,
                        close_return=close_return,
                        profit=profit,
                        profit_pct=profit_pct,
                    ).where(Trade.open_order_id == row.open_order_id).execute()
                    print(
                        f"\033[32m ✅ EXECUTED SELL ORDER: Symbol: [{order_detail['symbol']}], Asked price [{order_detail['average']}], Asked amount [{order_detail['amount']}], Profit [{profit:.2f} USDT], Profit [{profit_pct:.2f}%]\033[39m"
                    )
        except Exception as e:
            print("check_pending_orders() for sell orders failed")
            print(e)

    def get_all_balances(self):
        bal = {}
        results = {}
        symbols = []
        total = 0
        main_currency = self.bot.strategy.main_currency
        balances = self._api.fetch_balance()

        for item in balances["free"].items():
            if item[1] > 0:
                if item[0] != main_currency:
                    symbols.append(f"{item[0]}/{main_currency}")
                bal[item[0]] = item[1]

        tickers = self._api.fetch_tickers(symbols)

        for item in bal.items():
            if item[0] == main_currency:
                total += item[1]
                results[main_currency] = {
                    "Available": "{:.2f}".format(round(item[1], 2)),
                    "Est USDT": "{:.2f}".format(round(item[1], 2)),
                }
            else:
                estimated_value = (
                    item[1] * tickers[f"{item[0]}/{main_currency}"]["close"]
                )
                total += estimated_value
                if estimated_value > 1:
                    results[item[0]] = {
                        "Available": item[1],
                        f"Est {main_currency}": "{:.2f}".format(
                            round(estimated_value, 2)
                        ),
                    }
        results["Total"] = {
            "Tradable": "{:.2f}".format(round(self.get_balance(main_currency), 2)),
            f"Total {main_currency}": "{:.2f}".format(round(total, 2)),
        }
        return results

    @staticmethod
    def calculate_profit(
        open_cost: float,
        amount_available: float,
        close_price: float,
        is_long=True,
        trading_fee_rate: Optional[float] = 0.001,
    ):
        profit = 0
        profit_pct = 0
        if is_long:
            close_return = close_price * amount_available * (1 - trading_fee_rate)
            profit = close_return - open_cost
            profit_pct = (close_return / open_cost) - 1
        else:
            close_return = close_price * amount_available * (1 - trading_fee_rate)
            profit = open_cost - close_return
            profit_pct = (open_cost / close_return) - 1
        return [profit, profit_pct, close_return]