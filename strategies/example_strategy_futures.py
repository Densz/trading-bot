from tradingbot.strategy import IStrategy
from tradingbot.customtypes import Tick, Info
from tradingbot.logger import logger

from pandas.core.frame import DataFrame
import talib.abstract as ta

RSI_STRATEGY = {
    "id": "RSI",
    "rsi_lower_level": 50,
    "rsi_high_level": 50,
}

RSI_STRATEGY_2 = {
    "id": "RSI2",
    "rsi_lower_level": 50,
    "rsi_high_level": 50,
}


class Strategy(IStrategy):
    """
    MUST HAVE VARIABLES AND FUNCTIONS BELOW
    TO BE ABLE TO RUN THE BOT
    Variables:
        - main_currency
        - amount_allocated
        - tickers
    Functions:
        - __init__
        - add_indicators
        - on_tick

    """

    main_currency = "USDT"
    amount_allocated = 1000

    tickers = [
        ("DOGEUSDT", "1m"),
        # ("DOGE/USDT", "15m"),
        # ("BNB/USDT", "1m"),
        # ("BTC/USDT", "1m"),
        # ("ETH/USDT", "1m"),
        # ("LTC/USDT", "1m"),
        # ("LINK/USDT", "1m"),
        # ("BCH/USDT", "1m"),
    ]

    def __init__(self, bot) -> None:
        IStrategy.__init__(self, bot)

    def add_indicators(self, df: DataFrame) -> DataFrame:
        df["RSI"] = ta.RSI(df["close"])

        macd = ta.MACD(df, window_fast=12, window_slow=26)
        df["macd"] = macd["macd"]
        df["macdsignal"] = macd["macdsignal"]
        df["macdhist"] = macd["macdhist"]

        df["sma200"] = ta.SMA(df, timeperiod=200)

        df["atr"] = ta.ATR(df["high"], df["low"], df["close"], timeperiod=14)

        return df

    def on_tick(self, df: DataFrame, tick: Tick, info: Info) -> None:
        logger.info("Run strat 1")
        limit = 13.5  # USDT
        amount = limit / tick["close"]
        # open_trade = self.database.has_trade_open(
        #     symbol=tick["symbol"],
        #     strategy=RSI_STRATEGY["id"],
        #     timeframe=info["timeframe"],
        # )
        last_bar = df.loc[0]
        logger.info(last_bar["RSI"])
        balance = self.exchange.get_balance("USDT")
        # print(balance)
        tickers = self.exchange.get_tickers(["BTCUSDT", "ETHUSDT", "DOGEUSDT"])
        # print(tickers)
        tradable_balance = self.exchange.get_tradable_balance()
        print(tradable_balance)

        # # There is no open trade
        # if open_trade == None:
        #     if last_bar["RSI"] < RSI_STRATEGY["rsi_lower_level"]:
        #         self.exchange.create_buy_order(
        #             symbol=tick["symbol"],
        #             strategy=RSI_STRATEGY["id"],
        #             timeframe=info["timeframe"],
        #             amount=amount,
        #             price=tick["close"],
        #             stop_loss=tick["close"] * 0.95,
        #             take_profit=tick["close"] * 1.05,
        #         )
        # # When there is open trade
        # else:
        #     if last_bar["RSI"] > RSI_STRATEGY["rsi_high_level"]:
        #         self.exchange.create_sell_order(
        #             symbol=tick["symbol"],
        #             strategy=RSI_STRATEGY["id"],
        #             timeframe=info["timeframe"],
        #             price=tick["close"],
        #             reason="RSI OVER 70",
        #         )
        # pass
