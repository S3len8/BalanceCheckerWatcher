import asyncio

from binance import calc_balance_binance

calc_balance_binance = asyncio.run(calc_balance_binance())
print(calc_balance_binance) 