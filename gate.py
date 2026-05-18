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

API_KEY = os.getenv("GATE_API_KEY")
API_SECRET = os.getenv("GATE_API_SECRET") 
SPOT_AND_FUTURES_BASE_URL = "https://api.gateio.ws"


async def get_balance_spot():
    """ Function for getting balance spot Gate """
    endpoint = "/api/v4/spot/accounts"
    timestamp = str(int(time.time()))
    method = "GET"
    query_string = ""  # В данном запросе параметров нет
    body_string = ""  # Для GET запроса тело пустое
    hashed_body = hashlib.sha512(body_string.encode('utf-8')).hexdigest()
    sign_string = f"{method}\n{endpoint}\n{query_string}\n{hashed_body}\n{timestamp}"
    signature = hmac.new(
        API_SECRET.encode('utf-8'),
        sign_string.encode('utf-8'),
        hashlib.sha512,
    ).hexdigest()
    headers = {
        "Accept": "application/json",
        "KEY": API_KEY,
        "SIGN": signature,
        "Timestamp": timestamp,
        "Content-type": "application/json",
        "X-Gate-Size-Decimal": "1",
    }
    url = f"{SPOT_AND_FUTURES_BASE_URL}{endpoint}"
    response = requests.get(url, headers=headers)
    return response.json()


get_balance_spot = asyncio.run(get_balance_spot())
print(get_balance_spot)


async def get_balance_futures():
    """ Function for getting balance futures Gate """
    endpoint = "/api/v4/futures/usdt/accounts"
    timestamp = str(int(time.time()))
    method = "GET"
    query_string = ""  # В данном запросе параметров нет
    body_string = ""  # Для GET запроса тело пустое
    hashed_body = hashlib.sha512(body_string.encode('utf-8')).hexdigest()
    sign_string = f"{method}\n{endpoint}\n{query_string}\n{hashed_body}\n{timestamp}"
    signature = hmac.new(
        API_SECRET.encode('utf-8'),
        sign_string.encode('utf-8'),
        hashlib.sha512,
    ).hexdigest()
    headers = {
        "Accept": "application/json",
        "KEY": API_KEY,
        "SIGN": signature,
        "Timestamp": timestamp,
        "Content-type": "application/json",
        "X-Gate-Size-Decimal": "1",
    }
    url = f"{SPOT_AND_FUTURES_BASE_URL}{endpoint}"
    response = requests.get(url, headers=headers).json()
    available = response["available"]
    total =  response.get("total")
    result = {"available": available, "total": total}
    return result


get_balance_futures = asyncio.run(get_balance_futures())
print(get_balance_futures) 


async def get_price(session, symbol):  
    """ Function for getting price Gate """ 
    if symbol == "USDT":
        return "1.0"
    url = f"https://api.gateio.ws/api/v4/spot/tickers?currency_pair={symbol}_USDT"
    async with session.get(url) as response:
        data = await response.json()
        for price in data:
            return price.get("last")


async def create_session_gate(symbols: list):
    """ Function for creating session Gate """
    async with aiohttp.ClientSession() as session:
        tasks = []
        for symbol_dict in symbols:
            symbol = symbol_dict["currency"]
            tasks.append(get_price(session, symbol))

        result = await asyncio.gather(*tasks)
        return result


create_session_gate = asyncio.run(create_session_gate(get_balance_spot))
print(create_session_gate)


async def sumarazing_assets_and_their_price(prices: list, symbols: list):
    """ Function for sumarazing assets and their price Gate """
    symbols_list = []
    for symbol in symbols:
        symbols_list.append(symbol["currency"])

    result = {}
    for symbol, price in zip(symbols_list, prices):
        result.update({symbol: price})

    return result


sumarazing_assets_and_their_price = asyncio.run(sumarazing_assets_and_their_price(prices=create_session_gate, symbols=get_balance_spot))
print(sumarazing_assets_and_their_price) 