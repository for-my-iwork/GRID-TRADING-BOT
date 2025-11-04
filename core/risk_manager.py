# core/risk_manager.py
"""
🤖 УПРАВЛЕНИЕ РИСКАМИ ДЛЯ GRID BOT
"""

from config import STOP_LOSS_PCT, MAX_DRAWDOWN_PCT, MAX_API_ERRORS

class RiskManager:
    """🤖 УПРАВЛЕНИЕ РИСКАМИ ДЛЯ GRID BOT"""
    
    def __init__(self):
        self.stop_loss_pct = STOP_LOSS_PCT
        self.max_drawdown_pct = MAX_DRAWDOWN_PCT
        self.max_api_errors = MAX_API_ERRORS
        self.stop_reason = None

    def check_stop_conditions(self, net_profit, initial_total_balance, api_errors, max_profit, max_drawdown):
        """🚨 ПРОВЕРКА УСЛОВИЙ ДЛЯ ОСТАНОВКИ"""
        self.stop_reason = None
        
        # Проверка ошибок API
        if api_errors >= self.max_api_errors:
            self.stop_reason = f"Слишком много ошибок API ({api_errors})"
            return True
            
        # Проверка стоп-лосса
        if net_profit < -abs(initial_total_balance * self.stop_loss_pct):
            self.stop_reason = f"Стоп-лосс ({self.stop_loss_pct*100}%)"
            return True
            
        # Проверка максимальной просадки
        if initial_total_balance > 0:
            current_drawdown = max_profit - net_profit
            drawdown_pct = (current_drawdown / initial_total_balance) * 100
            if drawdown_pct > (self.max_drawdown_pct * 100):
                self.stop_reason = f"Максимальная просадка ({self.max_drawdown_pct*100}%)"
                return True
            
        return False

    def get_stop_reason(self):
        """📋 ПОЛУЧЕНИЕ ПРИЧИНЫ ОСТАНОВКИ"""
        return self.stop_reason or "Неизвестно"

    def update_risk_parameters(self, stop_loss_pct=None, max_drawdown_pct=None):
        """⚙️ ОБНОВЛЕНИЕ ПАРАМЕТРОВ РИСК-МЕНЕДЖМЕНТА"""
        if stop_loss_pct is not None:
            self.stop_loss_pct = stop_loss_pct
        if max_drawdown_pct is not None:
            self.max_drawdown_pct = max_drawdown_pct

    def calculate_position_size(self, balance, risk_per_trade=0.01):
        """📏 РАСЧЕТ РАЗМЕРА ПОЗИЦИИ"""
        return balance * risk_per_trade

    def get_risk_summary(self):
        """📊 СВОДКА ПО РИСКАМ"""
        return {
            'stop_loss_pct': self.stop_loss_pct * 100,
            'max_drawdown_pct': self.max_drawdown_pct * 100,
            'max_api_errors': self.max_api_errors
        }
