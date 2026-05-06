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
print(get_balance_all_assets)


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