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
import urllib.parse

load_dotenv()

API_KEY = os.getenv("KUCOIN_API_KEY")
API_SECRET = os.getenv("KUCOIN_API_SECRET")
KUCOIN_PASSPHRASE = os.getenv("KUCOIN_PASSWORD")
SPOT_BASE_URL = "https://api.kucoin.com"
FUTURES_BASE_URL = "https://api-futures.kucoin.com"


async def get_balance_spot():
    """ Function for getting balance spot Kucoin """
    endpoint = "/api/v1/accounts"
    timestamp = str(int(time.time() * 1000))
    method = "GET"
    sign_string = f"{timestamp}{method}{endpoint}"
    signature = hmac.new(
        API_SECRET.encode('utf-8'),
        sign_string.encode('utf-8'),
        hashlib.sha256,
    ).digest()
    signature_base64 = base64.b64encode(signature).decode('utf-8')
    passphrase_sign = hmac.new(
        API_SECRET.encode('utf-8'),
        KUCOIN_PASSPHRASE.encode('utf-8'),
        hashlib.sha256,
    ).digest()
    passphrase_base64 = base64.b64encode(passphrase_sign).decode('utf-8')
    headers = {
        "KC-API-KEY": API_KEY,
        "KC-API-SIGN": signature_base64,
        "KC-API-TIMESTAMP": timestamp,
        "KC-API-PASSPHRASE": passphrase_base64,
        "KC-API-KEY-VERSION": "2",
        "Content-Type": "application/json",
    }
    url = f"{SPOT_BASE_URL}{endpoint}"
    response = requests.get(url, headers=headers).json()
    result = {}
    for data in response["data"]:
        result.update({data["currency"]: data["balance"]})
    return result


get_balance_spot = asyncio.run(get_balance_spot())
print(get_balance_spot)


async def get_balance_futures():
    """ Function for getting balance futures Kucoin """
    endpoint = "/api/v1/account-overview"
    timestamp = str(int(time.time() * 1000))
    method = "GET"
    sign_string = f"{timestamp}{method}{endpoint}"
    signature = hmac.new(
        API_SECRET.encode('utf-8'),
        sign_string.encode('utf-8'),
        hashlib.sha256,
    ).digest()
    signature_base64 = base64.b64encode(signature).decode('utf-8')
    passphrase_sign = hmac.new(
        API_SECRET.encode('utf-8'),
        KUCOIN_PASSPHRASE.encode('utf-8'),
        hashlib.sha256,
    ).digest()
    passphrase_base64 = base64.b64encode(passphrase_sign).decode('utf-8')
    headers = {
        "KC-API-KEY": API_KEY,
        "KC-API-SIGN": signature_base64,
        "KC-API-TIMESTAMP": timestamp,
        "KC-API-PASSPHRASE": passphrase_base64,
        "KC-API-KEY-VERSION": "2",
        "Content-Type": "application/json",
    }
    url = f"{FUTURES_BASE_URL}{endpoint}"
    response = requests.get(url, headers=headers).json()
    print(response)
    result = response["data"]["availableBalance"]
    return result


get_balance_futures = asyncio.run(get_balance_futures())
print(get_balance_futures) 


async def get_price(session, symbol):  
    """ Function for getting price Gate """ 
    if symbol == "USDT":
        return "1.0"
    url = f"https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={symbol}-USDT"
    async with session.get(url) as response:
        data = await response.json()
        current_price = data["data"]["price"]
        return current_price


async def create_session_kucoin(symbols: list):
    """ Function for creating session Kucoin """
    async with aiohttp.ClientSession() as session:
        tasks = []
        for symbol in symbols:
            print(symbol)
            tasks.append(get_price(session, symbol))

        result = await asyncio.gather(*tasks)
        return result


create_session_kucoin = asyncio.run(create_session_kucoin(get_balance_spot))
print(create_session_kucoin)


async def sumarazing_assets_and_their_price(prices: list, symbols: list):
    """ Function for sumarazing assets and their price Kucoin """
    result = {}
    for symbol, price, how_much in zip(symbols, prices, symbols.values()):
        result.update({symbol: float(price) * float(how_much)})

    return result


sumarazing_assets_and_their_price = asyncio.run(sumarazing_assets_and_their_price(prices=create_session_kucoin, symbols=get_balance_spot))
print(sumarazing_assets_and_their_price) 