import os
from dotenv import load_dotenv
import asyncio
import requests
import time
import hmac
import hashlib
import httpx
import aiohttp

load_dotenv()

API_KEY = os.getenv("BYBIT_API_KEY")
API_SECRET = os.getenv("BYBIT_API_SECRET")
SPOT_AND_FUTURES_BASE_URL = "https://api.bybit.com"


async def get_balance_spot():
    """ Function for getting current balances from Bybit,
        now function get information from spot and UTA """

    endpoint = "/v5/account/wallet-balance"
    # Для Bybit V5 параметры в GET запросе должны быть частью подписи
    account_type = "UNIFIED"  # Или "SPOT", если у вас не UTA аккаунт
    params = f"accountType={account_type}"

    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"

    # Формируем строку для подписи по правилам Bybit V5:
    # timestamp + api_key + recv_window + query_string
    val = timestamp + API_KEY + recv_window + params
    signature = hmac.new(
        API_SECRET.encode('utf-8'),
        val.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    headers = {
        "X-BAPI-API-KEY": API_KEY,
        "X-BAPI-SIGN": signature,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": recv_window,
    }

    url = f"{SPOT_AND_FUTURES_BASE_URL}{endpoint}?{params}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                text = await response.text()
                return {"error": response.status, "message": text}


balance_spot = asyncio.run(get_balance_spot())
print(balance_spot)


async def get_available_balance():
    """ Function for getting available balances from Bybit """
    for balance in balance_spot.get("result").get("list"):
        available_balance = balance["totalAvailableBalance"]
        return available_balance


async def get_total_equity():
    """ Function for getting all money on Bybit """
    for balance in balance_spot.get("result").get("list"):
        totalEquity = balance["totalEquity"]
        return totalEquity


async def get_assets():
    """ Function for getting all assets from Bybit BTC, ETH, XRP and etc. """
    result = {}
    for balance in balance_spot.get("result").get("list"):
        for coins in balance["coin"]:
            coin = coins["coin"]
            usdValue = coins["usdValue"]
            result.update({coin: usdValue})
    return result


available_balance = asyncio.run(get_available_balance())
print(available_balance)
total_equity = asyncio.run(get_total_equity())
print(total_equity)
assets = asyncio.run(get_assets())
print(assets)