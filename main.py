import os
from dotenv import load_dotenv
import asyncio
import requests
import time
import hmac
import hashlib
import httpx

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
SPOT_BASE_URL = "https://api.binance.com"
FUTURES_BASE_URL = "https://fapi.binance.com"


async def get_balance_binance_spot():
    """ Function for getting current balances from Binance,
        now function get information from spot and earn """
    endpoint = "/api/v3/account"
    # 1. Create timestamp (Binance потребує часову мітку в мілісекундах)
    timestamp = int(time.time() * 1000)
    query_string = f"timestamp={timestamp}"

    # 2. Create Signature with Secret Key used for it
    signature = hmac.new(
        API_SECRET.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # 3. Final URL and headers
    url = f"{SPOT_BASE_URL}{endpoint}?{query_string}&signature={signature}"
    headers = {"X-MBX-APIKEY": API_KEY}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        data = response.json()
        # print(data)
        # Filtering coins which have in balance
        if "balances" in data:
            balances = [
                asset for asset in data["balances"]
                if float(asset["free"]) > 0 or float(asset["locked"]) > 0
            ]
            return balances
        return data

async def get_balance_futers():
    """ Function for getting current balances from Futures. """
    endpoint = "/fapi/v2/balance"
    # 1. Create timestamp (Binance потребує часову мітку в мілісекундах)
    timestamp = int(time.time() * 1000)
    query_string = f"timestamp={timestamp}"

    # 2. Create Signature with Secret Key used for it
    signature = hmac.new(
        API_SECRET.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # 3. Final URL and headers
    url = f"{FUTURES_BASE_URL}{endpoint}?{query_string}&signature={signature}"
    headers = {"X-MBX-APIKEY": API_KEY}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        data = response.json()

        for balance in data:
            data_balance = balance["balance"]
            if float(data_balance) > 0:
                return data_balance

        # Write list comperhension
        # balance = [balance_value for balance in data if (balance_value := float(balance["balance"])) > 0]

        # return balance


def calc_balance_binance():
    """ Function for calculating all money in Binance """
    pass

balance_spot = asyncio.run(get_balance_binance_spot())
print(balance_spot)
balance_futures = asyncio.run(get_balance_futers())
print(balance_futures)