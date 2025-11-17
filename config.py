# config.py
"""
Configuration module for Grid Trading Bot.

This module handles loading and validation of environment variables 
and configuration settings for the trading bot.
"""
import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# ==================== РЕЖИМ РАБОТЫ ====================
DEMO_MODE = True  # True для демо-торговли, False для реальной

# ==================== BYBIT НАСТРОЙКИ ====================
BYBIT_API_KEY = os.getenv("BYBIT_API_KEY", "").strip()
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET", "").strip()

# ==================== TELEGRAM НАСТРОЙКИ ====================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
TELEGRAM_POLLING_INTERVAL = 10   # Интервал проверки команд (секунды)
TELEGRAM_REPORT_INTERVAL = 3600 # Отчет каждый час

# ==================== ПАРАМЕТРЫ ТОРГОВЛИ ====================
SYMBOL = "BTCUSDT"              # Торговая пара
DEFAULT_ORDER_SIZE = 0.0002     # Размер ордера в BTC
DEFAULT_GRID_LEVELS = 5         # Количество уровней сетки
DEFAULT_GRID_SPACING = 0.003    # Расстояние между уровнями (0.3%)

# ==================== УПРАВЛЕНИЕ РИСКАМИ ====================
MAX_DRAWDOWN_PCT = 0.05         # Максимальная просадка (5%)
STOP_LOSS_PCT = 0.02            # Стоп-лосс (2%)
MAX_API_ERRORS = 100            # Максимальное количество ошибок API

# ==================== AI ОПТИМИЗАЦИЯ ====================
AI_ANALYSIS_TIMEFRAMES = ['1', '5', '15', '60']  # Таймфреймы в минутах
VOLATILITY_LOOKBACK = 100        # Период для анализа волатильности
MIN_SESSION_DURATION = 60        # Минимальное время сессии (минуты)
MAX_SESSION_DURATION = 20160     # Максимальное время сессии (минуты)

# ==================== НАСТРОЙКИ ЛОГИРОВАНИЯ ====================
LOG_RETENTION_DAYS = 7          # Хранить логи за последние 7 дней

# Комиссии по умолчанию (будут перезаписаны из API)
DEFAULT_MAKER_FEE = 0.001  # 0.1%
DEFAULT_TAKER_FEE = 0.001  # 0.1%

# Интервал обновления комиссий (в секундах)
COMMISSION_UPDATE_INTERVAL = 3600  # 1 час

# ==================== ПРОВЕРКА НАЛИЧИЯ КЛЮЧЕЙ ====================
def validate_config():
    """Проверяет, что все необходимые переменные загружены"""
    missing_vars = []
    if not BYBIT_API_KEY:
        missing_vars.append("BYBIT_API_KEY")
    if not BYBIT_API_SECRET:
        missing_vars.append("BYBIT_API_SECRET")
    if not TELEGRAM_TOKEN:
        missing_vars.append("TELEGRAM_TOKEN")
    if not TELEGRAM_CHAT_ID:
        missing_vars.append("TELEGRAM_CHAT_ID")
    if missing_vars:
        print(f"⚠️  ВНИМАНИЕ: Отсутствуют переменные окружения: {', '.join(missing_vars)}")
        print("   Убедитесь, что файл .env создан и содержит все необходимые ключи")
        return False
    print("✅ Все переменные окружения загружены успешно")
    return True

# Автопроверка при импорте модуля
CONFIG_VALID = validate_config()

if __name__ == "__main__":
    # Тестовый вывод конфигурации (без секретов)
    print("\n=== ТЕСТ КОНФИГУРАЦИИ ===")
    print(f"DEMO_MODE: {DEMO_MODE}")
    print(f"TELEGRAM_POLLING_INTERVAL: {TELEGRAM_POLLING_INTERVAL}")
    print(f"TELEGRAM_REPORT_INTERVAL: {TELEGRAM_REPORT_INTERVAL}")
    print(f"SYMBOL: {SYMBOL}")
    print(f"DEFAULT_ORDER_SIZE: {DEFAULT_ORDER_SIZE}")
    print(f"DEFAULT_GRID_LEVELS: {DEFAULT_GRID_LEVELS}")
    print(f"DEFAULT_GRID_SPACING: {DEFAULT_GRID_SPACING}")
    print(f"MAX_DRAWDOWN_PCT: {MAX_DRAWDOWN_PCT}")
    print(f"STOP_LOSS_PCT: {STOP_LOSS_PCT}")
    print(f"MAX_API_ERRORS: {MAX_API_ERRORS}")
    print(f"AI_ANALYSIS_TIMEFRAMES: {AI_ANALYSIS_TIMEFRAMES}")
    print(f"VOLATILITY_LOOKBACK: {VOLATILITY_LOOKBACK}")
    print(f"MIN_SESSION_DURATION: {MIN_SESSION_DURATION}")
    print(f"MAX_SESSION_DURATION: {MAX_SESSION_DURATION}")
    print(f"LOG_RETENTION_DAYS: {LOG_RETENTION_DAYS}")
    print(f"DEFAULT_MAKER_FEE: {DEFAULT_MAKER_FEE}")
    print(f"DEFAULT_TAKER_FEE: {DEFAULT_TAKER_FEE}")
    print(f"COMMISSION_UPDATE_INTERVAL: {COMMISSION_UPDATE_INTERVAL}")
    print(f"Конфигурация {'валидна' if config_valid else 'невалидна'}")
