# analytics/logger.py
"""
📊 ЛОГИРОВАНИЕ ДАННЫХ ТОРГОВЛИ
"""

import csv
import os
import json
from datetime import datetime

class DataLogger:
    """📊 ЛОГИРОВАНИЕ ДАННЫХ ТОРГОВЛИ"""
    
    def __init__(self):
        self.log_dir = None
        self.log_file = None
        self.commission_file = None
        self.ai_log_file = None

    def setup_logging(self):
        """📁 НАСТРОЙКА СИСТЕМЫ ЛОГИРОВАНИЯ"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_dir = f"bot_logs_{timestamp}"
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.log_file = os.path.join(self.log_dir, "trading_log.csv")
        self.orders_file = os.path.join(self.log_dir, "orders_log.json")
        self.error_log_file = os.path.join(self.log_dir, "errors.log")
        self.commission_file = os.path.join(self.log_dir, "commissions.csv")
        self.ai_log_file = os.path.join(self.log_dir, "ai_optimizations.csv")
        
        # Создаем заголовки CSV файлов
        with open(self.log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp', 'current_price', 'active_orders', 'executed_orders',
                'usdt_balance', 'btc_balance', 'net_profit', 'total_commission',
                'grid_count', 'time_left_min', 'api_errors'
            ])
        
        with open(self.commission_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'order_id', 'side', 'commission', 'total_commission'])
        
        with open(self.ai_log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp', 'volatility', 'price_change_pct', 
                'old_levels', 'new_levels', 'old_spacing_pct', 'new_spacing_pct'
            ])
        
        print(f"📁 Логирование настроено в папке: {self.log_dir}")

    def log_trading_data(self, data):
        """📝 ЛОГИРОВАНИЕ ДАННЫХ ТОРГОВЛИ"""
        try:
            with open(self.log_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    data.get('timestamp', ''),
                    data.get('current_price', 0),
                    data.get('active_orders', 0),
                    data.get('executed_orders', 0),
                    data.get('usdt_balance', 0),
                    data.get('btc_balance', 0),
                    data.get('net_profit', 0),
                    data.get('total_commission', 0),
                    data.get('grid_count', 0),
                    data.get('time_left_min', 0),
                    data.get('api_errors', 0)
                ])
        except Exception as e:
            print(f"❌ Ошибка логирования: {e}")

    def log_commission(self, commission_data):
        """💸 ЛОГИРОВАНИЕ КОМИССИЙ"""
        try:
            with open(self.commission_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    commission_data.get('timestamp', ''),
                    commission_data.get('order_id', ''),
                    commission_data.get('side', ''),
                    commission_data.get('commission', 0),
                    commission_data.get('total_commission', 0)
                ])
        except Exception as e:
            print(f"❌ Ошибка логирования комиссии: {e}")

    def log_ai_optimization(self, optimization_data):
        """🧠 ЛОГИРОВАНИЕ AI ОПТИМИЗАЦИЙ"""
        try:
            with open(self.ai_log_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    optimization_data.get('timestamp', ''),
                    optimization_data.get('volatility', 0),
                    optimization_data.get('price_change_pct', 0),
                    optimization_data.get('old_levels', 0),
                    optimization_data.get('new_levels', 0),
                    optimization_data.get('old_spacing', 0) * 100,
                    optimization_data.get('new_spacing', 0) * 100
                ])
        except Exception as e:
            print(f"❌ Ошибка логирования AI оптимизации: {e}")

    def log_error(self, error_data):
        """❌ ЛОГИРОВАНИЕ ОШИБОК"""
        try:
            with open(self.error_log_file, 'a') as f:
                f.write(f"{datetime.now().isoformat()} - {error_data}\n")
        except Exception as e:
            print(f"❌ Ошибка логирования ошибки: {e}")
