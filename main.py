import asyncio

import requests

async def get_balance_binance_spot():
    params = {API_KEY: API_KEY, API_SECRET: API_SECRET}
    balance = requests.get("https://api.binance.com/api/v3/balance", params=params).json()
    return balance.json()

balance = asyncio.run(get_balance_binance_spot())
print(balance)