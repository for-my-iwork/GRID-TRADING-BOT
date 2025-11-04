# utils/helpers.py
"""
🔧 ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ GRID BOT
"""

import time
from datetime import datetime, timedelta

def format_price(price):
    """💰 ФОРМАТИРОВАНИЕ ЦЕНЫ ДЛЯ ВЫВОДА"""
    return f"{price:,.1f}"

def format_balance(usdt_balance, btc_balance, btc_price):
    """💳 ФОРМАТИРОВАНИЕ БАЛАНСА"""
    total = usdt_balance + (btc_balance * btc_price)
    return f"{usdt_balance:.2f} USDT + {btc_balance:.6f} BTC = {total:.2f} USDT"

def calculate_running_time(start_time):
    """⏰ РАСЧЕТ ВРЕМЕНИ РАБОТЫ"""
    if start_time:
        running_seconds = time.time() - start_time
        hours = int(running_seconds // 3600)
        minutes = int((running_seconds % 3600) // 60)
        seconds = int(running_seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return "00:00:00"

def calculate_time_left(end_time):
    """⏱️ РАСЧЕТ ОСТАВШЕГОСЯ ВРЕМЕНИ"""
    time_left_seconds = end_time - time.time()
    if time_left_seconds <= 0:
        return "00:00"
    
    hours = int(time_left_seconds // 3600)
    minutes = int((time_left_seconds % 3600) // 60)
    return f"{hours:02d}:{minutes:02d}"

def format_percentage(value):
    """📊 ФОРМАТИРОВАНИЕ ПРОЦЕНТОВ"""
    return f"{value*100:.2f}%"

def safe_float_conversion(value, default=0.0):
    """🛡️ БЕЗОПАСНОЕ ПРЕОБРАЗОВАНИЕ В FLOAT"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int_conversion(value, default=0):
    """🛡️ БЕЗОПАСНОЕ ПРЕОБРАЗОВАНИЕ В INT"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def calculate_profit_percentage(initial_balance, current_balance):
    """📈 РАСЧЕТ ПРОЦЕНТА ПРИБЫЛИ"""
    if initial_balance == 0:
        return 0.0
    return ((current_balance - initial_balance) / initial_balance) * 100

def get_timestamp():
    """🕒 ПОЛУЧЕНИЕ ТЕКУЩЕЙ МЕТКИ ВРЕМЕНИ"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def format_duration(minutes):
    """⏱️ ФОРМАТИРОВАНИЕ ДЛИТЕЛЬНОСТИ"""
    hours = minutes // 60
    mins = minutes % 60
    if hours > 0:
        return f"{hours}ч {mins}м"
    return f"{mins}м"

def validate_parameters(grid_levels, order_size, grid_spacing, duration):
    """✅ ПРОВЕРКА ВАЛИДНОСТИ ПАРАМЕТРОВ"""
    errors = []
    
    if grid_levels < 1 or grid_levels > 10:
        errors.append("Количество уровней должно быть от 1 до 10")
    
    if order_size <= 0 or order_size > 0.01:
        errors.append("Размер ордера должен быть от 0.0001 до 0.01 BTC")
    
    if grid_spacing <= 0 or grid_spacing > 0.05:
        errors.append("Расстояние между уровнями должно быть от 0.1% до 5%")
    
    if duration < 1 or duration > 1440:
        errors.append("Время работы должно быть от 1 до 1440 минут")
    
    return errors
