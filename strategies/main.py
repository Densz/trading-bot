RSI_LOWER_LEVEL = 30
RSI_MIDDLE_LEVEL = 100


class Strategy():
    timeframe = "1h"
    startup_candles = 200
    tickers = ["BTC/USDT",
               "LINK/USDT"]
    main_currency = 'USDT'
    max_tradable_amount = 1000

    def on_init():
        print("on_init called")

    def on_deinit():
        print("de_init called")

    def on_tick(df):
        """
          Useful for stoploss or takeprofit
        """
        print("on_tick called")

    def on_new_candle(df):
        """
          Useful for stoploss or takeprofit
        """
        print("on_new_candle called")
