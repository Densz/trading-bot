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

    # def create_trade(self):
    #     print("create_trade")

    # def get_open_trades(self):
    #     print("get_open_orders")

    # def update_trade(self):
    #     print("update_trade")

    # def close_trade(self, trade_id):
    #     print("set_trade_as_done")

    # def _create_db(self):
    #     pass


class Trade(pw.Model):
    symbol = pw.CharField()

    status = pw.CharField(default="OPEN")  # enum(FILLED, CLOSED)

    open_rate = pw.FloatField()
    fee_open = pw.FloatField()

    close_rate = pw.FloatField(null=True)
    fee_close = pw.FloatField(null=True)

    stop_loss = pw.FloatField(null=True)
    take_profit = pw.FloatField(null=True)

    created_at = pw.DateTimeField(default=datetime.now)

    class Meta:
        database = db  # This model uses the "people.db" database.
