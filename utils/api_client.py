# utils/api_client.py
"""
🔧 КЛИЕНТ ДЛЯ РАБОТЫ С BYBIT API
"""

import time
from pybit.unified_trading import HTTP
from config import BYBIT_API_KEY, BYBIT_API_SECRET, DEMO_MODE

class APIClient:
    """🔧 КЛИЕНТ ДЛЯ РАБОТЫ С BYBIT API"""
    def __init__(self):
        """Инициализация клиента API"""
        self.session = HTTP(
            testnet=False,
            demo=DEMO_MODE,
            api_key=BYBIT_API_KEY,
            api_secret=BYBIT_API_SECRET,
            recv_window=15000
        )
        self.api_errors = 0
        self.max_retries = 5

    def get_fee_rate(self, symbol: str, category: str = "spot"):
        """💰 ПОЛУЧЕНИЕ КОМИССИЙ ПО ТОРГОВОЙ ПАРЕ"""
        try:
            # Используем правильное название метода - get_fee_rates (во множественном числе)
            fee_data = self.session.get_fee_rates(
                category=category,
                symbol=symbol
            )
            return fee_data
        except (ConnectionError, TimeoutError, KeyError, ValueError,
                TypeError) as e:
            print(f"❌ Ошибка получения комиссий через API: {e}")
            print("🔄 Использую стандартные комиссии 0.1%")
            # Возвращаем значения по умолчанию при ошибке
            return {
                'retCode': 0,
                'result': {
                    'list': [{
                        'symbol': symbol,
                        'makerFeeRate': '0.001',
                        'takerFeeRate': '0.001'
                    }]
                }
            }

    def robust_api_call(self, api_function, *args, **kwargs):
        """🔄 НАДЕЖНЫЙ ВЫЗОВ API С ПОВТОРНЫМИ ПОПЫТКАМИ"""
        retry_delay = 5
        for attempt in range(self.max_retries):
            try:
                result = api_function(*args, **kwargs)
                return result
            except (ConnectionError, TimeoutError, ValueError,
                    TypeError, KeyError) as e:
                self.api_errors += 1
                print(f"❌ Ошибка API (попытка {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    print(f"🔄 Повтор через {retry_delay} секунд...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    print("❌ Превышено максимальное количество попыток")
                    return None

    def get_current_price(self, symbol):
        """💰 ПОЛУЧЕНИЕ ТЕКУЩЕЙ ЦЕНЫ"""
        try:
            ticker = self.robust_api_call(
                self.session.get_tickers,
                category="spot",
                symbol=symbol
            )
            if (ticker and
                'result' in ticker and 
                'list' in ticker['result'] and 
                len(ticker['result']['list']) > 0 and
                'lastPrice' in ticker['result']['list'][0]):
                return float(ticker['result']['list'][0]['lastPrice'])
            return None
        except (KeyError, ValueError, TypeError) as e:
            print(f"❌ Ошибка получения цены: {e}")
            return None

    def get_balance(self):
        """💳 ПОЛУЧЕНИЕ БАЛАНСА КОШЕЛЬКА"""
        try:
            balance = self.robust_api_call(
                self.session.get_wallet_balance,
                accountType="UNIFIED"
            )
            if (not balance or
                'result' not in balance or 
                'list' not in balance['result'] or 
                len(balance['result']['list']) == 0 or
                'coin' not in balance['result']['list'][0]):
                return 0, 0
            usdt_balance = 0
            btc_balance = 0
            for coin in balance['result']['list'][0]['coin']:
                if coin.get('coin') == 'USDT':
                    usdt_balance = float(coin.get('walletBalance', 0))
                if coin.get('coin') == 'BTC':
                    btc_balance = float(coin.get('walletBalance', 0))
            return usdt_balance, btc_balance
        except (KeyError, ValueError, TypeError) as e:
            print(f"❌ Ошибка получения баланса: {e}")
            return 0, 00

    def place_order(self, symbol, side, order_type, qty, price, 
                   time_in_force="GTC"):
        """📦 РАЗМЕЩЕНИЕ ОРДЕРА"""
        try:
            order = self.robust_api_call(
                self.session.place_order,
                category="spot",
                symbol=symbol,
                side=side,
                orderType=order_type,
                qty=str(qty),
                price=str(price),
                timeInForce=time_in_force
            )
            return order
        except (ConnectionError, TimeoutError, ValueError, 
                TypeError) as e:
            print(f"❌ Ошибка размещения ордера: {e}")
            return None

    def cancel_all_orders(self, symbol):
        """🛑 ОТМЕНА ВСЕХ ОРДЕРОВ"""
        try:
            result = self.robust_api_call(
                self.session.cancel_all_orders,
                category="spot",
                symbol=symbol
            )
            return result
        except (ConnectionError, TimeoutError, ValueError,
                TypeError) as e:
            print(f"❌ Ошибка отмены ордеров: {e}")
            return None

    def get_open_orders(self, symbol):
        """📋 ПОЛУЧЕНИЕ СПИСКА ОТКРЫТЫХ ОРДЕРОВ"""
        try:
            orders = self.robust_api_call(
                self.session.get_open_orders,
                category="spot",
                symbol=symbol
            )
            return orders
        except (ConnectionError, TimeoutError, ValueError,
                TypeError) as e:
            print(f"❌ Ошибка получения открытых ордеров: {e}")
            return None
