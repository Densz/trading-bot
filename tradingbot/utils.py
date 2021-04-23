from typing import Tuple


def calculate_profit(
    open_cost: float,
    amount_available: float,
    close_price: float,
    is_long=True,
    trading_fee_rate: float = 0.001,
) -> Tuple[float, float, float]:
    if is_long:
        close_return = close_price * amount_available * (1 - trading_fee_rate)
        profit = close_return - open_cost
        profit_pct = (close_return / open_cost) - 1
        return (profit, profit_pct, close_return)
    else:
        close_return = close_price * amount_available * (1 - trading_fee_rate)
        profit = open_cost - close_return
        profit_pct = (open_cost / close_return) - 1
        return (profit, profit_pct, close_return)
