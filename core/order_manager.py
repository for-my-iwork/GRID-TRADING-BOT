"""
Order Manager v9.1 - ПОЛНОСТЬЮ ПЕРЕРАБОТАННЫЙ КОД
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Optional

from core.thread_safe import synchronized
from utils.bybit_client import BybitClient


class OrderManager:
    """Менеджер ордеров с полными исправлениями"""
    
    def __init__(self, bybit_client: BybitClient, config):
        self.client = bybit_client
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Конфигурация комиссий из config
        self.maker_fee_rate = getattr(config, 'MAKER_FEE_RATE', 0.0001)
        self.taker_fee_rate = getattr(config, 'TAKER_FEE_RATE', 0.0006)
        
        self.logger.info(f"Order Manager инициализирован. Комиссии: maker={self.maker_fee_rate}, taker={self.taker_fee_rate}")
    
    @synchronized
    def create_limit_buy_order(self, symbol: str, quantity: float, price: float) -> Optional[Dict]:
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
            
            if response and 'orderId' in response:
                self.logger.info(f"Создан LIMIT BUY ордер: {quantity} {symbol} по {price}")
                return {
                    'orderId': response['orderId'],
                    'symbol': symbol,
                    'side': 'BUY',
                    'price': price,
                    'quantity': quantity,
                    'timestamp': datetime.now()
                }
            else:
                self.logger.error(f"Не удалось создать BUY ордер. Ответ: {response}")
                return None
            
        except Exception as e:
            self.logger.error(f"Ошибка создания BUY ордера: {e}")
            return None
    
    @synchronized
    def create_limit_sell_order(self, symbol: str, quantity: float, price: float) -> Optional[Dict]:
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
            
            if response and 'orderId' in response:
                self.logger.info(f"Создан LIMIT SELL ордер: {quantity} {symbol} по {price}")
                return {
                    'orderId': response['orderId'],
                    'symbol': symbol,
                    'side': 'SELL',
                    'price': price,
                    'quantity': quantity,
                    'timestamp': datetime.now()
                }
            else:
                self.logger.error(f"Не удалось создать SELL ордер. Ответ: {response}")
                return None
            
        except Exception as e:
            self.logger.error(f"Ошибка создания SELL ордера: {e}")
            return None
    
    @synchronized
    def create_market_buy_order(self, symbol: str, quantity: float) -> Optional[Dict]:
        """Создание маркет ордера на покупку"""
        try:
            order_params = {
                'symbol': symbol,
                'side': 'Buy',
                'orderType': 'Market',
                'qty': str(quantity)
            }
            
            response = self.client.place_order(**order_params)
            
            if response and 'orderId' in response:
                self.logger.info(f"Создан MARKET BUY ордер: {quantity} {symbol}")
                return {
                    'orderId': response['orderId'],
                    'symbol': symbol,
                    'side': 'BUY',
                    'quantity': quantity,
                    'timestamp': datetime.now()
                }
            else:
                self.logger.error(f"Не удалось создать MARKET BUY ордер. Ответ: {response}")
                return None
            
        except Exception as e:
            self.logger.error(f"Ошибка создания MARKET BUY ордера: {e}")
            return None
    
    @synchronized
    def create_market_sell_order(self, symbol: str, quantity: float) -> Optional[Dict]:
        """Создание маркет ордера на продажу"""
        try:
            order_params = {
                'symbol': symbol,
                'side': 'Sell',
                'orderType': 'Market',
                'qty': str(quantity)
            }
            
            response = self.client.place_order(**order_params)
            
            if response and 'orderId' in response:
                self.logger.info(f"Создан MARKET SELL ордер: {quantity} {symbol}")
                return {
                    'orderId': response['orderId'],
                    'symbol': symbol,
                    'side': 'SELL',
                    'quantity': quantity,
                    'timestamp': datetime.now()
                }
            else:
                self.logger.error(f"Не удалось создать MARKET SELL ордер. Ответ: {response}")
                return None
            
        except Exception as e:
            self.logger.error(f"Ошибка создания MARKET SELL ордера: {e}")
            return None
    
    @synchronized
    def cancel_order(self, symbol: str, order_id: str) -> bool:
        """Отмена ордера"""
        try:
            cancel_params = {
                'symbol': symbol,
                'orderId': order_id
            }
            
            response = self.client.cancel_order(**cancel_params)
            
            if response:
                self.logger.info(f"Ордер {order_id} отменен")
                return True
            else:
                self.logger.error(f"Не удалось отменить ордер {order_id}")
                return False
            
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
            
            if response:
                self.logger.info(f"Все ордера для {symbol} отменены")
                return True
            else:
                self.logger.error(f"Не удалось отменить все ордера для {symbol}")
                return False
            
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
            
            if response and 'status' in response:
                return response['status']
            else:
                self.logger.warning(f"Не удалось получить статус ордера {order_id}")
                return 'UNKNOWN'
            
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса ордера {order_id}: {e}")
            return 'UNKNOWN'
    
    @synchronized
    def get_active_orders(self, symbol: str) -> List[Dict]:
        """Получение списка активных ордеров"""
        try:
            response = self.client.get_open_orders(symbol=symbol)
            
            if response and 'list' in response:
                return response.get('list', [])
            else:
                self.logger.warning(f"Не удалось получить активные ордера для {symbol}")
                return []
            
        except Exception as e:
            self.logger.error(f"Ошибка получения активных ордеров для {symbol}: {e}")
            return []
    
    @synchronized
    def get_order_history(self, symbol: str, limit: int = 100) -> List[Dict]:
        """Получение истории ордеров"""
        try:
            response = self.client.get_order_history(symbol=symbol, limit=limit)
            
            if response and 'list' in response:
                return response.get('list', [])
            else:
                self.logger.warning(f"Не удалось получить историю ордеров для {symbol}")
                return []
            
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
            
            if new_price is not None:
                modify_params['price'] = str(new_price)
            if new_quantity is not None:
                modify_params['qty'] = str(new_quantity)
            
            response = self.client.modify_order(**modify_params)
            
            if response:
                self.logger.info(f"Ордер {order_id} изменен")
                return True
            else:
                self.logger.error(f"Не удалось изменить ордер {order_id}")
                return False
            
        except Exception as e:
            self.logger.error(f"Ошибка изменения ордера {order_id}: {e}")
            return False
    
    def calculate_order_commission(self, order_type: str, quantity: float, 
                                 price: float, is_maker: bool = True) -> float:
        """Расчет комиссии для ордера"""
        try:
            trade_value = quantity * price
            fee_rate = self.maker_fee_rate if is_maker else self.taker_fee_rate
            commission = trade_value * fee_rate
            
            self.logger.debug(f"Рассчитана комиссия: {commission:.6f} для ордера {order_type}")
            return commission
            
        except Exception as e:
            self.logger.error(f"Ошибка расчета комиссии: {e}")
            return 0.0
    
    @synchronized
    def get_filled_quantity(self, symbol: str, order_id: str) -> float:
        """Получение исполненного количества"""
        try:
            order_info = self.client.get_order(symbol=symbol, orderId=order_id)
            
            if order_info and 'executedQty' in order_info:
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
    
    def get_fee_rates(self) -> Dict[str, float]:
        """Получение текущих ставок комиссий"""
        return {
            'maker_fee_rate': self.maker_fee_rate,
            'taker_fee_rate': self.taker_fee_rate
        }
