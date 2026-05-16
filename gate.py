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
MEXC_ID = os.getenv("MEXC_ID")
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
    response = requests.get(url, headers=headers)
    return response.json()


get_balance_futures = asyncio.run(get_balance_futures())
print(get_balance_futures)  