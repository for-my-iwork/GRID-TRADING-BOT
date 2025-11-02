"""
Order Manager v9.1 - Управление ордерами с исправлениями
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Optional

from core.thread_safe import synchronized
from utils.bybit_client import BybitClient


class OrderManager:
    """Менеджер ордеров с Thread Safety"""
    
    def __init__(self, bybit_client: BybitClient):
        self.client = bybit_client
        self.logger = logging.getLogger(__name__)
        
        # Конфигурация комиссий
        self.maker_fee_rate = 0.0001  # 0.01%
        self.taker_fee_rate = 0.0006  # 0.06%
        
        self.logger.info("Order Manager инициализирован")
    
    @synchronized
    def create_limit_buy_order(self, symbol: str, quantity: float, price: float) -> Dict:
        """Создание лимитного ордера на покупку"""
        try:
            order_params = {
                'symbol': symbol,
                'side': 'Buy',
                'orderType': 'Limit',
                'qty': str(quantity),
                'price': str(price),
                'timeInForce': 'GTC'
            }
            
            response = self.client.place_order(**order_params)
            
            self.logger.info(f"Создан LIMIT BUY ордер: {quantity} {symbol} по {price}")
            return {
                'orderId': response['orderId'],
                'symbol': symbol,
                'side': 'BUY',
                'price': price,
                'quantity': quantity,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка создания BUY ордера: {e}")
            raise
    
    @synchronized
    def create_limit_sell_order(self, symbol: str, quantity: float, price: float) -> Dict:
        """Создание лимитного ордера на продажу"""
        try:
            order_params = {
                'symbol': symbol,
                'side': 'Sell',
                'orderType': 'Limit',
                'qty': str(quantity),
                'price': str(price),
                'timeInForce': 'GTC'
            }
            
            response = self.client.place_order(**order_params)
            
            self.logger.info(f"Создан LIMIT SELL ордер: {quantity} {symbol} по {price}")
            return {
                'orderId': response['orderId'],
                'symbol': symbol,
                'side': 'SELL',
                'price': price,
                'quantity': quantity,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка создания SELL ордера: {e}")
            raise
    
    @synchronized
    def create_market_buy_order(self, symbol: str, quantity: float) -> Dict:
        """Создание маркет ордера на покупку"""
        try:
            order_params = {
                'symbol': symbol,
                'side': 'Buy',
                'orderType': 'Market',
                'qty': str(quantity)
            }
            
            response = self.client.place_order(**order_params)
            
            self.logger.info(f"Создан MARKET BUY ордер: {quantity} {symbol}")
            return {
                'orderId': response['orderId'],
                'symbol': symbol,
                'side': 'BUY',
                'quantity': quantity,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка создания MARKET BUY ордера: {e}")
            raise
    
    @synchronized
    def create_market_sell_order(self, symbol: str, quantity: float) -> Dict:
        """Создание маркет ордера на продажу"""
        try:
            order_params = {
                'symbol': symbol,
                'side': 'Sell',
                'orderType': 'Market',
                'qty': str(quantity)
            }
            
            response = self.client.place_order(**order_params)
            
            self.logger.info(f"Создан MARKET SELL ордер: {quantity} {symbol}")
            return {
                'orderId': response['orderId'],
                'symbol': symbol,
                'side': 'SELL',
                'quantity': quantity,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка создания MARKET SELL ордера: {e}")
            raise
    
    @synchronized
    def cancel_order(self, symbol: str, order_id: str) -> bool:
        """Отмена ордера"""
        try:
            cancel_params = {
                'symbol': symbol,
                'orderId': order_id
            }
            
            response = self.client.cancel_order(**cancel_params)
            
            self.logger.info(f"Ордер {order_id} отменен")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка отмены ордера {order_id}: {e}")
            return False
    
    @synchronized
    def cancel_all_orders(self, symbol: str) -> bool:
        """Отмена всех ордеров для символа"""
        try:
            cancel_params = {
                'symbol': symbol
            }
            
            response = self.client.cancel_all_orders(**cancel_params)
            
            self.logger.info(f"Все ордера для {symbol} отменены")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка отмены всех ордеров для {symbol}: {e}")
            return False
    
    @synchronized
    def get_order_status(self, symbol: str, order_id: str) -> str:
        """Получение статуса ордера"""
        try:
            order_params = {
                'symbol': symbol,
                'orderId': order_id
            }
            
            response = self.client.get_order(**order_params)
            return response['status']
            
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса ордера {order_id}: {e}")
            return 'UNKNOWN'
    
    @synchronized
    def get_active_orders(self, symbol: str) -> List[Dict]:
        """Получение списка активных ордеров"""
        try:
            response = self.client.get_open_orders(symbol=symbol)
            return response.get('list', [])
            
        except Exception as e:
            self.logger.error(f"Ошибка получения активных ордеров для {symbol}: {e}")
            return []
    
    @synchronized
    def get_order_history(self, symbol: str, limit: int = 100) -> List[Dict]:
        """Получение истории ордеров"""
        try:
            response = self.client.get_order_history(symbol=symbol, limit=limit)
            return response.get('list', [])
            
        except Exception as e:
            self.logger.error(f"Ошибка получения истории ордеров для {symbol}: {e}")
            return []
    
    @synchronized
    def modify_order(self, symbol: str, order_id: str, new_price: float = None, 
                    new_quantity: float = None) -> bool:
        """Изменение ордера"""
        try:
            modify_params = {
                'symbol': symbol,
                'orderId': order_id
            }
            
            if new_price:
                modify_params['price'] = str(new_price)
            if new_quantity:
                modify_params['qty'] = str(new_quantity)
            
            response = self.client.modify_order(**modify_params)
            
            self.logger.info(f"Ордер {order_id} изменен")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка изменения ордера {order_id}: {e}")
            return False
    
    def calculate_order_commission(self, order_type: str, quantity: float, 
                                 price: float, is_maker: bool = True) -> float:
        """Расчет комиссии для ордера"""
        trade_value = quantity * price
        fee_rate = self.maker_fee_rate if is_maker else self.taker_fee_rate
        commission = trade_value * fee_rate
        
        self.logger.debug(f"Рассчитана комиссия: {commission:.6f} для ордера {order_type}")
        return commission
    
    @synchronized
    def get_filled_quantity(self, symbol: str, order_id: str) -> float:
        """Получение исполненного количества"""
        try:
            order_status = self.get_order_status(symbol, order_id)
            if order_status == 'FILLED':
                order_info = self.client.get_order(symbol=symbol, orderId=order_id)
                return float(order_info.get('executedQty', 0))
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Ошибка получения исполненного количества для {order_id}: {e}")
            return 0.0
    
    def wait_for_order_fill(self, symbol: str, order_id: str, 
                          timeout: int = 30) -> bool:
        """Ожидание исполнения ордера"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_order_status(symbol, order_id)
            
            if status == 'FILLED':
                self.logger.info(f"Ордер {order_id} исполнен")
                return True
            elif status in ['CANCELED', 'REJECTED', 'EXPIRED']:
                self.logger.warning(f"Ордер {order_id} не исполнен, статус: {status}")
                return False
            
            time.sleep(1)  # Пауза между проверками
        
        self.logger.warning(f"Таймаут ожидания исполнения ордера {order_id}")
        return False
