import os
from dotenv import load_dotenv
import asyncio
import requests
import time
import hmac
import hashlib
import httpx
import aiohttp
import base64

load_dotenv()

API_KEY = os.getenv("BITGET_API_KEY")
API_SECRET = os.getenv("BITGET_API_SECRET")
PASSWORD = os.getenv("BITGET_PASSWORD")
SPOT_AND_FUTURES_BASE_URL = "https://api.bitget.com"


async def get_balance_all_assets():
    """ Function for get requests to Bitget for all assets """
    endpoint = "/api/v2/account/all-account-balance"
    timestamp = str(int(time.time() * 1000))
    prehash_str = f"{timestamp}GET{endpoint}"

    # ВАЖНО: Bitget V2 требует Base64
    mac = hmac.new(
        API_SECRET.encode('utf-8'),
        prehash_str.encode('utf-8'),
        hashlib.sha256
    )
    signature = base64.b64encode(mac.digest()).decode('utf-8')

    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": PASSWORD,
        "Content-Type": "application/json"
    }

    url = f"{SPOT_AND_FUTURES_BASE_URL}{endpoint}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return await response.json()


get_balance_all_assets = asyncio.run(get_balance_all_assets())
# print(get_balance_all_assets)


async def get_balance_spot():
    """ Function for get requests to Bitget for spot assets """
    endpoint = "/api/v2/spot/account/assets"
    timestamp = str(int(time.time() * 1000))
    prehash_str = f"{timestamp}GET{endpoint}"

    # ВАЖНО: Bitget V2 требует Base64
    mac = hmac.new(
        API_SECRET.encode('utf-8'),
        prehash_str.encode('utf-8'),
        hashlib.sha256
    )
    signature = base64.b64encode(mac.digest()).decode('utf-8')

    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": PASSWORD,
        "Content-Type": "application/json"
    }

    url = f"{SPOT_AND_FUTURES_BASE_URL}{endpoint}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return await response.json()


get_balance_spot = asyncio.run(get_balance_spot())
print(get_balance_spot)


async def list_symbols_spot():
    """ Function for listing all available symbols in spot Bitget """
    list_symbols_spot = [symbol['coin'] for symbol in get_balance_spot.get("data")]
    return list_symbols_spot


list_symbols_spot = asyncio.run(list_symbols_spot())
print(list_symbols_spot)


async def free_assets():
    free_assets = [price.get("available") for price in get_balance_spot.get("data")]
    return free_assets

free_assets = asyncio.run(free_assets())
print(free_assets)


async def calc_all_assets():
    """ Function for calculation assets Bitget """
    result = {}
    for data in get_balance_all_assets.get("data"):
        spot = data['accountType']
        spot_usdt = data['usdtBalance']
        result.update({spot: spot_usdt})
    return result

calc_all_assets = asyncio.run(calc_all_assets())
print(calc_all_assets)


async def get_price(session, symbol) -> float:
    """ Function for getting prices from Binance """
    if symbol == "USDT":
        return "1.0"
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
    async with session.get(url) as response:
        data = await response.json()
        if data.get("code") == -1121:
            return "0.0"
        return data.get("price")


async def create_session_bitget(symbols_list: list):
    """ Function for creating sessions for get current prices in Bitget exchange """
    async with aiohttp.ClientSession() as session:
        tasks = []
        for symbol in symbols_list:
            tasks.append(get_price(session, symbol))

        result = await asyncio.gather(*tasks)
        return result


create_session_bitget = asyncio.run(create_session_bitget(list_symbols_spot))
print(create_session_bitget)

async def calc_price_spot():
    """ Function for calculation price spot assets Bitget """
    result = []
    for price, symbol in zip(free_assets, create_session_bitget):
        calc_balance = float(price) * float(symbol)
        result.append(calc_balance)
    return result


calc_price_spot = asyncio.run(calc_price_spot())
print(calc_price_spot)


async def compare_price_with_symbols_spot():
    """ Function for comparing price spot assets Bitget """
    result = {}
    for price, symbol in zip(calc_price_spot, list_symbols_spot):
        result.update({symbol: price})
    return result


compare_price_with_symbols_spot = asyncio.run(compare_price_with_symbols_spot())
print(compare_price_with_symbols_spot)