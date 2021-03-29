import peewee as pw
from datetime import datetime
from tradingbot.config import get_config

config = get_config()

db = pw.SqliteDatabase('sandbox.db' if config['dry_run'] ==
                       True else 'live.db')


class Database:
    def __init__(self, config):
        self._config = config

        db.connect()
        try:
            if (config['dry_run'] == True):
                db.drop_tables([Trade])
            db.create_tables([Trade])
        except:
            pass

    def get_open_orders(self):
        pass

    def get_strategy_used_balance(self):
        pass

    def get_profit(self, strategy_name=None):
        pass

    def has_trade_open(self, symbol):
        pass


class Trade(pw.Model):
    exchange = pw.CharField(default='binance')

    symbol = pw.CharField()
    strategy = pw.CharField(null=False)
    timeframe = pw.CharField(null=False)

    is_long = pw.BooleanField(default=True)

    amount_start = pw.FloatField(null=False)
    amount_available = pw.FloatField(null=True)
    amount_end = pw.FloatField(null=True)

    open_order_id = pw.CharField(null=False)
    open_order_status = pw.CharField(null=False, default="open")
    open_price_requested = pw.FloatField(null=True)
    open_price = pw.FloatField(null=True)
    open_fee_rate = pw.FloatField(default=0.001)
    open_fee = pw.FloatField(null=True)
    open_date = pw.DateTimeField(null=False)

    close_order_id = pw.CharField(null=False)
    close_order_status = pw.BooleanField(default="open")
    close_price_requested = pw.FloatField(null=True)
    close_price = pw.FloatField(null=True)
    close_fee_rate = pw.FloatField(default=0.001)
    close_fee = pw.FloatField(null=True)
    close_date = pw.DateTimeField(null=False)

    initial_stop_loss = pw.FloatField(null=True, default=0.0)
    current_stop_loss = pw.FloatField(null=True, default=0.0)
    take_profit = pw.FloatField(null=True)

    profit = pw.FloatField(null=True)
    profit_pct = pw.FloatField(null=True)
    sell_reason = pw.CharField(null=True)

    created_at = pw.DateTimeField(default=datetime.now)

    class Meta:
        database = db
