import ccxt
import ccxt.async_support as ccxt_async
from ccxt.base.decimal_to_precision import (ROUND_DOWN, ROUND_UP, TICK_SIZE, TRUNCATE,
                                            decimal_to_precision)
from typing import Dict


class Exchange:
    def __init__(self, config) -> None:
        self._api: ccxt.Exchange = ccxt.binance({
            **config['binance']
        })
        self._api.load_markets()
        self._api_async: ccxt_async.Exchange = None

    def get_market_symbols(self):
        return self._api.symbols

    def create_buy_order(self, stop_loss, at_price):
        print("place_order")

    def update_order(self, order_id, stop_loss: None, take_profit: None):
        print("update_order")

    def create_sell_order(self, order_id, at_price):
        print("sell_order")

    def cancel_order(self, order_id):
        print("cancel_order")

    def get_available_amount():
        print("get_available_amount")


# from tradingbot.exchange import Exchange

# test = Exchange()
# binance = ccxt.binance({
#     'apiKey': 'uR7IjNwUAB5GpocH79xWmavd34Ow74Q4juonLOabUAnjecjInccG0LedVg0xNvuW',
#     'secret': 'AfwfH2JqGFc4D5GJy77k9Dtcyl0h3fY0sqKdOExTNKLkwXNk4ifOQImUZOWW1ViN',
#     'timeout': 30000,
#     'enableRateLimit': True,
# })

# symbols = ['BTC/USDT', 'ETH/USDT']

# market = binance.load_markets()
# binance_available_symbols = binance.symbols
# print(binance_available_symbols.index('BTC/USDT'))
# print(binance.fetch_order_book(binance.symbols[0]))
# print(binance.fetch_ticker('BTC/USD'))
# print(binance.fetch_trades('LTC/USDT'))

# print(binance.fetch_balance())


# sell one ฿ for market price and receive $ right now
# print(binance.id, binance.create_market_sell_order('BTC/USD', 1))

# limit buy BTC/EUR, you pay €2500 and receive ฿1  when the order is closed
# print(exmo.id, exmo.create_limit_buy_order('BTC/EUR', 1, 2500.00))

# pass/redefine custom exchange-specific order params: type, amount, price, flags, etc...
# kraken.create_market_buy_order('BTC/USD', 1, {'trading_agreement': 'agree'})
