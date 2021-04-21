from pprint import pprint
from typing import Optional
import peewee as pw
from playhouse.sqlite_ext import *
from datetime import datetime

from telegram.bot import Bot
from tradingbot.config import get_config

config = get_config()

db = pw.SqliteDatabase("sandbox.db" if config["paper_mode"] == True else "live.db")


class Database:
    def __init__(self, bot: Bot):
        self.bot: Bot = bot

        db.connect()
        try:
            # if config["paper_mode"] == True:
            #     db.drop_tables([Trade])
            db.create_tables([Trade])
        except:
            pass

    def update_trade(
        self,
        trade_id: int,
        stoploss: Optional[float] = None,
        takeprofit: Optional[float] = None,
        data=None,
    ) -> None:
        trade = Trade.select().where(Trade.id == trade_id).execute()

        if len(trade) == 0:
            print(f"ERROR: Could not update trade because id [{trade_id}] not found")
            return

        Trade.update(
            current_stop_loss=stoploss if stoploss else trade[0].current_stop_loss,
            take_profit=takeprofit if takeprofit else trade[0].take_profit,
            data=data if data else None,
        ).where(Trade.id == trade_id).execute()

        pass

    def has_trade_open(self, symbol: str, strategy: str, timeframe: str):
        query = (
            Trade.select()
            .where(
                Trade.symbol == symbol,
                Trade.exchange == self.bot.config["exchange"],
                Trade.timeframe == timeframe,
                Trade.strategy == strategy,
                (
                    (Trade.open_order_status == "open")
                    | (Trade.open_order_status == "closed")
                ),
                Trade.close_order_status == None,
            )
            .dicts()
        )
        if len(query) >= 1:
            return query[0]
        return None

    def get_strategy_used_balance(self):
        pass

    def get_profit(self, strategy_name=None):
        pass

    def get_open_orders(
        self, symbol: Optional[str] = "", strategy: str = "", timeframe: str = ""
    ):
        open_orders = (
            Trade.select()
            .where(
                Trade.symbol == symbol if symbol else Trade.symbol != None,
                Trade.timeframe == timeframe if timeframe else Trade.symbol != None,
                Trade.strategy == strategy if strategy else Trade.strategy != None,
                Trade.exchange == self.bot.config["exchange"],
                Trade.open_order_status == "closed",
                Trade.close_order_status == None,
            )
            .execute()
        )
        if len(open_orders) == 0:
            return None
        return open_orders

    def get_used_amount(self):
        open_orders = (
            Trade.select(pw.fn.SUM(Trade.open_cost).alias("sum"))
            .where(
                Trade.exchange == self.bot.config["exchange"],
                (
                    (Trade.open_order_status == "closed")
                    | (Trade.open_order_status == "open")
                ),
                Trade.close_order_status == None,
            )
            .execute()
        )
        if len(open_orders) == 0:
            return 0
        if open_orders[0].sum == None:
            return 0
        return open_orders[0].sum


class Trade(pw.Model):
    exchange = pw.CharField(default="binance")

    symbol = pw.CharField()
    strategy = pw.CharField(null=False)
    timeframe = pw.CharField(null=False)

    is_long = pw.BooleanField(default=True)

    amount_requested = pw.FloatField(null=False)
    amount_available = pw.FloatField(null=False)

    open_order_id = pw.CharField(null=False, unique=True)
    open_order_status = pw.CharField(null=False, default="open")
    open_price_requested = pw.FloatField(null=False)
    open_price = pw.FloatField(null=True)
    open_fee_rate = pw.FloatField(null=True)
    open_fee = pw.FloatField(null=True)
    open_date = pw.DateTimeField(null=False)
    open_cost = pw.FloatField(null=True)

    close_order_id = pw.CharField(null=True, unique=True)
    close_order_status = pw.CharField(null=True)
    close_price_requested = pw.FloatField(null=True)
    close_price = pw.FloatField(null=True)
    close_fee_rate = pw.FloatField(null=True)
    close_fee = pw.FloatField(null=True)
    close_date = pw.DateTimeField(null=True)
    close_return = pw.FloatField(null=True)

    initial_stop_loss = pw.FloatField(null=True, default=0.0)
    current_stop_loss = pw.FloatField(null=True, default=0.0)
    take_profit = pw.FloatField(null=True)

    profit = pw.FloatField(null=True)
    profit_pct = pw.FloatField(null=True)
    sell_reason = pw.CharField(null=True)

    data = JSONField(null=True)

    created_at = pw.DateTimeField(default=datetime.now)

    class Meta:
        database = db
