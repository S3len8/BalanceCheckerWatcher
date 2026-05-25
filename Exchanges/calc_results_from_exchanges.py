import asyncio

from binance import calc_balance_binance
from bybit import get_total_equity
from bitget import get_all_assets
from gate import get_all_assets_gate
from kucoin import calc_all_usdt
from mexc import calc_USDT

calc_balance_binance = asyncio.run(calc_balance_binance())
# print(calc_balance_binance)
total_equity = asyncio.run(get_total_equity())
# print(total_equity)
get_all_assets = asyncio.run(get_all_assets())
# print(get_all_assets)
get_all_assets_gate = asyncio.run(get_all_assets_gate())
# print(get_all_assets_gate)
calc_all_usdt = asyncio.run(calc_all_usdt())
# print(calc_all_usdt)
calc_USDT = asyncio.run(calc_USDT())
# print(calc_USDT)


async def calculation_all_USDT():
    """ Function for calculation all USDT """
    result = (float(calc_balance_binance)
              + float(total_equity)
              + float(get_all_assets)
              + float(get_all_assets_gate)
              + float(calc_all_usdt)
              + float(calc_USDT))
    return result


calculation_all_USDT = asyncio.run(calculation_all_USDT())
print(calculation_all_USDT) 