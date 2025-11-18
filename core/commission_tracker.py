# core/commission_tracker.py
"""
Commission Tracker for Bybit Grid Trading Bot
Трекинг реальных комиссий через Bybit API
"""

import logging
import time
from typing import Dict, Optional
from utils.api_client import APIClient

class CommissionTracker:
    def __init__(self, api_client: APIClient, symbol: str, category: str = "spot"):
        self.logger = logging.getLogger(__name__)
        self.api_client = api_client
        self.symbol = symbol
        self.category = category
        self.maker_fee = 0.001  # Значение по умолчанию
        self.taker_fee = 0.001  # Значение по умолчанию
        self.last_update = None

    def fetch_fee_rates(self) -> Optional[Dict]:
        """
        Запрос реальных комиссий через Bybit API
        
        Returns:
            Dict с данными комиссий или None при ошибке
        """
        try:
            response = self.api_client.get_fee_rate(
                symbol=self.symbol,
                category=self.category
            )
            print(f"🔧 Ответ от API комиссий: {response}")  # Для отладки
            if response and response.get('retCode') == 0:
                fee_list = response.get('result', {}).get('list', [])
                if fee_list and len(fee_list) > 0:
                    fee_data = fee_list[0]
                    return fee_data
                else:
                    self.logger.warning("Пустой список комиссий в ответе API")
                    return None
            else:
                error_msg = response.get('retMsg', 'Unknown error') if response else 'No response'
                self.logger.warning(f"Ошибка запроса комиссий: {error_msg}")
                return None
        except Exception as e:
            self.logger.error(f"Ошибка получения комиссий: {str(e)}")
            return None

    def update_commission_rates(self) -> bool:
        """
        Обновление кэшированных значений комиссий
        
        Returns:
            bool: Успешно ли обновление
        """
        fee_data = self.fetch_fee_rates()
        if fee_data:
            # Обрабатываем как строковые, так и числовые значения
            maker_fee_str = fee_data.get('makerFeeRate', str(self.maker_fee))
            taker_fee_str = fee_data.get('takerFeeRate', str(self.taker_fee))
            self.maker_fee = float(maker_fee_str)
            self.taker_fee = float(taker_fee_str)
            self.last_update = time.time()
            self.logger.info(
                f"✅ Комиссии обновлены: maker={self.maker_fee:.6f}, "
                f"taker={self.taker_fee:.6f}"
            )
            return True
        else:
            self.logger.warning(
                "⚠️ Не удалось обновить комиссии, используются значения по умолчанию"
            )
            return False

    def calculate_maker_commission(self, quantity: float, price: float) -> float:
        """
        Расчет комиссии для maker ордера
        
        Args:
            quantity: Количество актива
            price: Цена
            
        Returns:
            float: Размер комиссии в базовой валюте
        """
        trade_value = quantity * price
        return trade_value * self.maker_fee

    def calculate_taker_commission(self, quantity: float, price: float) -> float:
        """
        Расчет комиссии для taker ордера
        
        Args:
            quantity: Количество актива
            price: Цена
            
        Returns:
            float: Размер комиссии в базовой валюте
        """
        trade_value = quantity * price
        return trade_value * self.taker_fee

    def get_current_rates(self) -> Dict[str, float]:
        """
        Получение текущих значений комиссий
        
        Returns:
            Dict с текущими maker и taker комиссиями
        """
        return {
            'maker_fee': self.maker_fee,
            'taker_fee': self.taker_fee,
            'last_update': self.last_update
        }
