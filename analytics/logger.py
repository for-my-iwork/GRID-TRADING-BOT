# analytics/logger.py
"""
📊 ЛОГИРОВАНИЕ ДАННЫХ ТОРГОВЛИ
"""

import csv
import os
import json
import time
from datetime import datetime
import tempfile
import shutil
from typing import Dict, Any, Optional

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
        with open(self.log_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp', 'current_price', 'active_orders', 'executed_orders',
                'usdt_balance', 'btc_balance', 'net_profit', 'total_commission',
                'grid_count', 'time_left_min', 'api_errors'
            ])
        with open(self.commission_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'order_id', 'side', 'commission', 'total_commission'])
        with open(self.ai_log_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp', 'volatility', 'price_change_pct', 
                'old_levels', 'new_levels', 'old_spacing_pct', 'new_spacing_pct'
            ])
        print(f"📁 Логирование настроено в папке: {self.log_dir}")

    def log_trading_data(self, data):
        """📝 ЛОГИРОВАНИЕ ДАННЫХ ТОРГОВЛИ"""
        try:
            with open(self.log_file, 'a', encoding='utf-8', newline='') as f:
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
            with open(self.commission_file, 'a', encoding='utf-8', newline='') as f:
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
            with open(self.ai_log_file, 'a', encoding='utf-8', newline='') as f:
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
            with open(self.error_log_file, 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now().isoformat()} - {error_data}\n")
        except Exception as e:
            print(f"❌ Ошибка логирования ошибки: {e}")


class StateManager:
    """🔄 МЕНЕДЖЕР СОСТОЯНИЯ БОТА"""
    def __init__(self, state_file: str = "bot_state.json"):
        self.state_file = state_file
        self.backup_file = f"{state_file}.backup"

    def save_state(self, state_data: Dict[str, Any]) -> bool:
        """
        Атомарное сохранение состояния бота
        """
        try:
            # Создаем временный файл для атомарной записи
            with tempfile.NamedTemporaryFile(mode='w', delete=False,
                                           suffix='.tmp', encoding='utf-8') as tmp_file:
                json.dump(state_data, tmp_file, indent=2, ensure_ascii=False)
                tmp_file.flush()
                os.fsync(tmp_file.fileno())
            # Создаем backup текущего состояния
            if os.path.exists(self.state_file):
                shutil.copy2(self.state_file, self.backup_file)
            # Атомарная замена файла
            shutil.move(tmp_file.name, self.state_file)
            print("✅ State saved successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to save state: {e}")
            # Пытаемся восстановить из backup
            if os.path.exists(self.backup_file):
                try:
                    shutil.copy2(self.backup_file, self.state_file)
                    print("✅ Restored state from backup")
                except Exception as backup_error:
                    print(f"❌ Failed to restore from backup: {backup_error}")
            return False

    def load_state(self) -> Optional[Dict[str, Any]]:
        """
        Загрузка состояния с валидацией и восстановлением при повреждении
        """
        state_data = None
        # Пытаемся загрузить основной файл
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                # Базовая валидация структуры
                if self._validate_state(state_data):
                    print("✅ State loaded successfully from main file")
                    return state_data
                else:
                    print("⚠️ State validation failed, trying backup")
                    state_data = None
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️ Failed to load main state file: {e}")
                state_data = None
        # Пытаемся загрузить backup
        if not state_data and os.path.exists(self.backup_file):
            try:
                with open(self.backup_file, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                if self._validate_state(state_data):
                    # Восстанавливаем основной файл из backup
                    shutil.copy2(self.backup_file, self.state_file)
                    print("✅ State restored from backup file")
                    return state_data
            except (json.JSONDecodeError, IOError) as e:
                print(f"❌ Failed to load backup state: {e}")
        print("ℹ️ No valid state found, starting fresh")
        return None

    def _validate_state(self, state_data: Dict[str, Any]) -> bool:
        """
        Валидация загруженного состояния
        """
        try:
            required_fields = ['version', 'timestamp', 'bot_data']
            if not all(field in state_data for field in required_fields):
                return False
            # Проверяем типы критических данных
            bot_data = state_data.get('bot_data', {})
            if not isinstance(bot_data, dict):
                return False
            # Проверяем обязательные поля в bot_data
            required_bot_fields = [
                'session_start_time', 'session_end_time', 'monitoring_duration',
                'active_order_ids', 'executed_orders_count', 'grid_count'
            ]
            for field in required_bot_fields:
                if field not in bot_data:
                    print(f"⚠️ Missing required bot_data field: {field}")
                    return False
            # Проверяем корректность времени
            current_time = time.time()
            session_end_time = bot_data.get('session_end_time')
            if session_end_time and session_end_time < current_time:
                print("⚠️ Session end time has passed, state is expired")
                return False
            return True
        except Exception as e:
            print(f"❌ State validation error: {e}")
            return False

    def clear_state(self) -> bool:
        """
        Очистка состояния только при явном завершении работы
        """
        try:
            # Состояние очищается только в следующих случаях:
            # 1. Явная команда /shutdown
            # 2. Завершение сессии по времени
            # 3. Аварийная остановка
            # НЕ очищается при простой остановке systemd службы!
            if os.path.exists(self.state_file):
                os.remove(self.state_file)
                print("✅ State cleared successfully")
            if os.path.exists(self.backup_file):
                os.remove(self.backup_file)
                print("✅ Backup state cleared successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to clear state: {e}")
            return False

    def save_state_only(self) -> bool:
        """
        Сохранение состояния без очистки (для systemd остановки)
        """
        try:
            # Этот метод должен вызываться при graceful shutdown через systemd
            # чтобы сохранить состояние для последующего восстановления
            current_state = self.load_state()
            if current_state:
                return self.save_state(current_state)
            return False
        except Exception as e:
            print(f"❌ Failed to save state for restart: {e}")
            return False

# Глобальный экземпляр для обратной совместимости
_state_manager = StateManager()

def save_state(state_data: Dict[str, Any]) -> bool:
    return _state_manager.save_state(state_data)

def load_state() -> Optional[Dict[str, Any]]:
    return _state_manager.load_state()

def clear_state() -> bool:
    return _state_manager.clear_state()

def save_state_only() -> bool:
    """Новая функция для сохранения состояния без очистки"""
    return _state_manager.save_state_only()
