# commission_tracker.py
import logging
from typing import Dict, Optional
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime


@dataclass
class CommissionRate:
    maker_fee: Decimal
    taker_fee: Decimal
    symbol: str

class CommissionTracker:
    def __init__(self, bybit_client):
        self.client = bybit_client
        self.commission_rates: Dict[str, CommissionRate] = {}
        self.logger = logging.getLogger(__name__)
        
    async def initialize_commission_rates(self, symbols: list):
        """Инициализация комиссионных ставок для символов"""
        for symbol in symbols:
            try:
                response = await self.client.get_fee_rate(
                    category="spot",
                    symbol=symbol
                )
                
                if response['retCode'] == 0:
                    fee_info = response['result']['list'][0]
                    self.commission_rates[symbol] = CommissionRate(
                        maker_fee=Decimal(str(fee_info['makerFeeRate'])),
                        taker_fee=Decimal(str(fee_info['takerFeeRate'])),
                        symbol=symbol
                    )
                    self.logger.info(f"Commission rates loaded for {symbol}: "
                                   f"maker={self.commission_rates[symbol].maker_fee}, "
                                   f"taker={self.commission_rates[symbol].taker_fee}")
                else:
                    self.logger.warning(f"Failed to get fee rate for {symbol}, using defaults")
                    # Стандартные комиссии Bybit Spot
                    self.commission_rates[symbol] = CommissionRate(
                        maker_fee=Decimal('0.001'),  # 0.1%
                        taker_fee=Decimal('0.001'),  # 0.1%
                        symbol=symbol
                    )
                    
            except Exception as e:
                self.logger.error(f"Error loading commission rates for {symbol}: {e}")
                # Fallback to default rates
                self.commission_rates[symbol] = CommissionRate(
                    maker_fee=Decimal('0.001'),
                    taker_fee=Decimal('0.001'),
                    symbol=symbol
                )
    
    def calculate_commission(self, symbol: str, executed_volume: Decimal, 
                           price: Decimal, is_maker: bool) -> Decimal:
        """Расчет комиссии для исполненного ордера"""
        if symbol not in self.commission_rates:
            self.logger.warning(f"No commission rate for {symbol}, using default")
            rate = Decimal('0.001')
        else:
            rate = (self.commission_rates[symbol].maker_fee if is_maker 
                   else self.commission_rates[symbol].taker_fee)
        
        commission = executed_volume * price * rate
        self.logger.info(f"Commission calculated: {commission:.6f} for {symbol}, "
                        f"{'maker' if is_maker else 'taker'} rate: {rate}")
        return commission
