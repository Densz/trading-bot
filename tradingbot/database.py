import peewee as pw
from datetime import datetime

DRY_RUN = False

db = pw.SqliteDatabase('sqlite.db' if DRY_RUN == False else 'sandbox.db')

print("Ok")


class BaseModel(pw.Model):
    class Meta:
        database = db


class User(BaseModel):
    username = pw.CharField(unique=True)


class Tweet(BaseModel):
    user = pw.ForeignKeyField(User, backref='tweets')
    message = pw.TextField()
    created_date = pw.DateTimeField(default=datetime.now)
    is_published = pw.BooleanField(default=True)


db.connect()
db.create_tables([User, Tweet])

charlie = User.create(username='charlssside')

# No need to set `is_published` or `created_date` since they
# will just use the default values we specified.
Tweet.create(user=charlie, message='My first tweet')

# A simple query selecting a user.
User.get(User.username == 'charlie')

# Get tweets created by one of several users.
usernames = ['charlie', 'huey', 'mickey']
users = User.select().where(User.username.in_(usernames))
tweets = Tweet.select().where(Tweet.user.in_(users))

# We could accomplish the same using a JOIN:
tweets = (Tweet
          .select()
          .join(User)
          .where(User.username.in_(usernames)))

# How many tweets were published today?
tweets_today = (Tweet
                .select()
                .where(
                    (Tweet.created_date >= datetime.date.today()) &
                    (Tweet.is_published == True))
                .count())

# Paginate the user table and show me page 3 (users 41-60).
User.select().order_by(User.username).paginate(3, 20)

# Order users by the number of tweets they've created:
tweet_ct = pw.fn.Count(Tweet.id)
users = (User
         .select(User, tweet_ct.alias('ct'))
         .join(Tweet, pw.JOIN.LEFT_OUTER)
         .group_by(User)
         .order_by(tweet_ct.desc()))

# Do an atomic update
pw.Counter.update(count=pw.Counter.count +
                  1).where(pw.Counter.url == pw.request.url)

# class Trade(BaseModel):
#     id = pw.Index(unique=True)
#     symbol = pw.CharField()

#     open_rate = pw.FloatField()
#     fee_open = pw.FloatField()

#     close_rate = pw.FloatField()
#     fee_close = pw.FloatField()

#     stoploss = pw.FloatField()
#     takeprofit = pw.FloatField()

#     created_at = pw.DateTimeField()
#     updated_at = pw.DateTimeField()


# class Database:
#     def __init__(self, config):
#         self._sql = None
#         self._config = config

#     def create_trade(self):
#         print("create_trade")

#     def get_open_trades(self):
#         print("get_open_orders")

#     def update_trade(self):
#         print("update_trade")

#     def close_trade(self, trade_id):
#         print("set_trade_as_done")

#     def _create_db(self):
#         pass
