# commission_tracker.py
"""
Точный учет комиссий Bybit с интеграцией Fee Rate API
"""

from datetime import datetime
import threading
from typing import Dict, List
import logging
from utils.bybit_client import BybitClient

class CommissionTracker:
    def __init__(self, bybit_client: BybitClient):
        self.client = bybit_client
        self.logger = logging.getLogger(__name__)
        
        # Thread-safe хранилище комиссий
        self._lock = threading.RLock()
        self.commission_history: List[Dict] = []
        
        # Актуальные ставки комиссий
        self.maker_fee_rate = 0.0001  # 0.01%
        self.taker_fee_rate = 0.0006  # 0.06%
        
    def update_fee_rates(self, symbol: str = "BTCUSDT"):
        """Обновление ставок комиссий через Bybit API"""
        try:
            # Получаем актуальные комиссии через API
            fee_info = self.client.get_fee_rate(symbol=symbol)
            
            with self._lock:
                self.maker_fee_rate = float(fee_info.get('makerFeeRate', self.maker_fee_rate))
                self.taker_fee_rate = float(fee_info.get('takerFeeRate', self.taker_fee_rate))
                
            self.logger.info(f"Updated fee rates - Maker: {self.maker_fee_rate:.4%}, Taker: {self.taker_fee_rate:.4%}")
            
        except Exception as e:
            self.logger.warning(f"Failed to update fee rates, using defaults: {e}")

    def calculate_commission(self, order_type: str, quantity: float, price: float, is_maker: bool = True) -> float:
        """Расчет комиссии для ордера"""
        trade_value = quantity * price
        
        with self._lock:
            fee_rate = self.maker_fee_rate if is_maker else self.taker_fee_rate
            commission = trade_value * fee_rate
            
        return commission

    def record_commission(self, order_id: str, symbol: str, commission: float, 
                         order_type: str, timestamp: datetime = None):
        """Запись комиссии в историю"""
        if timestamp is None:
            timestamp = datetime.now()
            
        record = {
            'timestamp': timestamp,
            'order_id': order_id,
            'symbol': symbol,
            'commission': commission,
            'order_type': order_type
        }
        
        with self._lock:
            self.commission_history.append(record)
            
        self.logger.debug(f"Recorded commission: {commission:.6f} for order {order_id}")

    def get_total_commissions(self, symbol: str = None) -> float:
        """Получение общей суммы комиссий"""
        with self._lock:
            if symbol:
                commissions = [c['commission'] for c in self.commission_history 
                             if c['symbol'] == symbol]
            else:
                commissions = [c['commission'] for c in self.commission_history]
                
        return sum(commissions)

    def get_commission_report(self) -> Dict:
        """Отчет по комиссиям"""
        with self._lock:
            total_commissions = self.get_total_commissions()
            daily_commissions = self._get_daily_commissions()
            
        return {
            'total_commissions': total_commissions,
            'daily_commissions': daily_commissions,
            'current_maker_rate': self.maker_fee_rate,
            'current_taker_rate': self.taker_fee_rate
        }

    def _get_daily_commissions(self) -> Dict[str, float]:
        """Комиссии по дням"""
        daily = {}
        with self._lock:
            for record in self.commission_history:
                date_str = record['timestamp'].strftime('%Y-%m-%d')
                daily[date_str] = daily.get(date_str, 0) + record['commission']
                
        return daily
