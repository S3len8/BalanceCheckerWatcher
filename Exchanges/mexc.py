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

API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")
MEXC_ID = os.getenv("MEXC_ID")
SPOT_AND_FUTURES_BASE_URL = "https://api.mexc.com"
FUTURES = "https://contract.mexc.com"


async def get_mexc_balance_direct(api_key: str, secret_key: str) -> dict:
    """
    Получает баланс спотового аккаунта напрямую через официальный API MEXC (v3).
    """
    endpoint = "/api/v3/account"

    # 1. Генерируем timestamp в миллисекундах (MEXC требует синхронизации времени)
    timestamp = int(time.time() * 1000)

    # Подготавливаем параметры запроса (query parameters)
    params = {
        'timestamp': timestamp,
        'recvWindow': 5000  # Окно задержки запроса в мс
    }

    # 2. Кодируем параметры в строку запроса (query string)
    query_string = urllib.parse.urlencode(params)

    # 3. Создаем подпись (HMAC SHA256) с использованием Secret Key
    signature = hmac.new(
        secret_key.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # Добавляем подпись в параметры запроса
    params['signature'] = signature

    # Заголовки запроса (API-ключ передается в заголовке X-MEXC-APIKEY)
    headers = {
        'X-MEXC-APIKEY': api_key,
        'Content-Type': 'application/json'
    }

    # 4. Отправляем GET-запрос
    url = f"{SPOT_AND_FUTURES_BASE_URL}{endpoint}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()

                    # Парсим ответ и оставляем только ненулевые балансы
                    balances = {}
                    for asset in data.get('balances', []):
                        free = float(asset.get('free', 0))
                        locked = float(asset.get('locked', 0))
                        total = free + locked

                        if total > 0:
                            balances[asset['asset']] = {
                                'free': f"{free:.7f}",
                                'locked': locked,
                                'total': total
                            }
                    return balances
                else:
                    error_text = await response.text()
                    print(f"Ошибка API (Код {response.status}): {error_text}")
                    return {}

        except aiohttp.ClientError as e:
            print(f"Ошибка сети: {e}")
            return {}


get_balance_direct = asyncio.run(get_mexc_balance_direct(API_KEY, API_SECRET))
# print(get_balance_direct)


async def get_current_price(session, symbol):
    """ Function for getting current price from exchange """
    if symbol == "USDT":
        return "1.0"
    url = f"https://api.mexc.com/api/v3/ticker/price?symbol={symbol}USDT"
    async with session.get(url) as response:
        data = await response.json()
        if data.get("price") == None:
            return "0.0"
        return data.get("price")


async def create_session_mexc_price(get_balance_direct: dict):
    """ Function for creating session """
    async with aiohttp.ClientSession() as session:
        tasks = []

        for symbol in get_balance_direct.keys():
            tasks.append(get_current_price(session, symbol))

        results = await asyncio.gather(*tasks)
        return results


create_session_mexc_price = asyncio.run(create_session_mexc_price(get_balance_direct))
# print(create_session_mexc_price)


async def free_assets_mexc():
    """ Function for listing free assets in MEXC """
    result = []
    assets = get_balance_direct.values()
    for symbol in assets:
        result.append(symbol["free"])
    return result


free_assets_mexc = asyncio.run(free_assets_mexc())
# print(free_assets_mexc)


async def calc_balance_spot():
    """ Function for calculating balance spot """
    balance = {}
    # symbols = [symbol for symbol in get_balance_direct().keys()]
    for price, assets, symbol in zip(create_session_mexc_price, free_assets_mexc, get_balance_direct.keys()):
        balance.update({symbol: f"{float(price) * float(assets):.7f}"})
    return balance


calc_balance_spot = asyncio.run(calc_balance_spot())
# print(calc_balance_spot)


async def get_balance_futures(api_key: str, secret_key: str):
    """ Function for getting balance futures MEXC """
    endpoint = "/api/v1/private/account/assets"
    # 1. Геруємо timestamp (мілісекунди)
    timestamp = str(int(time.time() * 1000))

    # 2. Формуємо рядок для підпису за стандартом Contract API:
    # Рядок підпису = API_KEY + TIMESTAMP + [QUERY_PARAMS/BODY]
    # Оскільки у нас GET без параметрів, додаємо тільки ключ і час
    sign_str = api_key + timestamp

    # 3. Створюємо підпис HMAC SHA256
    signature = hmac.new(
        secret_key.encode('utf-8'),
        sign_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # 4. Заголовки для CONTRACT API (відрізняються від SPOT)
    headers = {
        'ApiKey': api_key,
        'Request-Time': timestamp,
        'Signature': signature,
        'Content-Type': 'application/json'
    }

    url = f"{FUTURES}{endpoint}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()

                    # Структура відповіді ф'ючерсів відрізняється від споту
                    # Дані зазвичай знаходяться в data['data']
                    balances = {}
                    assets = data.get('data', [])

                    for asset in assets:
                        # У ф'ючерсах поля: availableBalance та frozenBalance
                        available = float(asset.get('availableBalance', 0))
                        frozen = float(asset.get('frozenBalance', 0))
                        total = available + frozen

                        if total > 0:
                            balances[asset["currency"]] = {
                                'free': f"{available:.4f}",
                                'locked': f"{frozen:.4f}",
                                'total': f"{total:.4f}"
                            }
                    return balances
                else:
                    error_text = await response.text()
                    print(f"Помилка API (Код {response.status}): {error_text}")
                    return {}

        except aiohttp.ClientError as e:
            print(f"Помилка мережі: {e}")
            return {}


get_balance_futures = asyncio.run(get_balance_futures(API_KEY, API_SECRET))
# print(get_balance_futures) 


async def calc_USDT():
    """ Function for calculating USDT """
    result = []
    for value in calc_balance_spot.values():
        result.append(float(value))

    for value in get_balance_futures.values():
        free = value["free"]
        locked = value["locked"]
        total = value["total"]
        result.append(float(free) + float(locked) + float(total))

    return sum(result)


# calc_USDT = asyncio.run(calc_USDT())
# print(calc_USDT) 