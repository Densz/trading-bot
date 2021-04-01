from pprint import pprint
import peewee as pw
from datetime import datetime
from tradingbot.config import get_config

config = get_config()

db = pw.SqliteDatabase('sandbox.db' if config['paper_mode'] ==
                       True else 'live.db')


class Database:
    def __init__(self, config, strategy):
        self._config = config
        self._strategy = strategy

        db.connect()
        try:
            if (config['paper_mode'] == True):
                db.drop_tables([Trade])
            db.create_tables([Trade])
        except:
            pass

    def has_trade_open(self, symbol: str):
        query = Trade.select().where(
            Trade.symbol == symbol,
            Trade.exchange == self._config['exchange'],
            Trade.timeframe == self._strategy.timeframe,
            Trade.strategy == self._strategy.strategy_params['id'],
            ((Trade.open_order_status == 'open') |
             (Trade.open_order_status == 'closed')),
            Trade.close_order_status == None,
        ).dicts()
        if (len(query) >= 1):
            return query[0]
        return None

    def get_strategy_used_balance(self):
        pass

    def get_profit(self, strategy_name=None):
        pass

    def get_open_orders(self, symbol):
        query = Trade.select().where(
            Trade.symbol == symbol,
            Trade.exchange == self._config['exchange'],
            Trade.timeframe == self._strategy.timeframe,
            Trade.strategy == self._strategy.strategy_params['id'],
            Trade.open_order_status == 'closed',
            Trade.close_order_status == None,
        ).dicts()
        if (len(query) > 0):
            return query
        return None


class Trade(pw.Model):
    exchange = pw.CharField(default='binance')

    symbol = pw.CharField()
    strategy = pw.CharField(null=False)
    timeframe = pw.CharField(null=False)

    is_long = pw.BooleanField(default=True)

    amount = pw.FloatField(null=False)

    open_order_id = pw.CharField(null=False, unique=True)
    open_order_status = pw.CharField(null=False, default="open")
    open_price_requested = pw.FloatField(null=True)
    open_price = pw.FloatField(null=True)
    open_fee_rate = pw.FloatField(default=0.001)
    open_fee = pw.FloatField(null=True)
    open_date = pw.DateTimeField(null=False)
    open_cost = pw.FloatField(null=True)

    close_order_id = pw.CharField(null=True, unique=True)
    close_order_status = pw.CharField(null=True)
    close_price_requested = pw.FloatField(null=True)
    close_price = pw.FloatField(null=True)
    close_fee_rate = pw.FloatField(default=0.001)
    close_fee = pw.FloatField(null=True)
    close_date = pw.DateTimeField(null=True)
    close_cost = pw.FloatField(null=True)

    initial_stop_loss = pw.FloatField(null=True, default=0.0)
    current_stop_loss = pw.FloatField(null=True, default=0.0)
    take_profit = pw.FloatField(null=True)

    profit = pw.FloatField(null=True)
    profit_pct = pw.FloatField(null=True)
    sell_reason = pw.CharField(null=True)

    created_at = pw.DateTimeField(default=datetime.now)

    class Meta:
        database = db
