# config.py
# Конфигурация Grid Trading Bot v9.2

# ==================== РЕЖИМ РАБОТЫ ====================
DEMO_MODE = True  # True для демо-торговли, False для реальной

# ==================== BYBIT API КЛЮЧИ ====================
BYBIT_API_KEY = "7sgdqpHkCOVHJ9h5IE"
BYBIT_API_SECRET = "pO9jp5elzvyn8UxwU3UIaLoCUqX3Y9ICVJHZ"

# ==================== TELEGRAM НАСТРОЙКИ ====================
TELEGRAM_TOKEN = "8070249499:AAEpc4O6Wm6vsXa-dXksXNIhshY3GJq9wqY"
TELEGRAM_CHAT_ID = "284000238"

# ==================== ПАРАМЕТРЫ ТОРГОВЛИ ====================
SYMBOL = "BTCUSDT"              # Торговая пара
DEFAULT_ORDER_SIZE = 0.0002     # Размер ордера в BTC
DEFAULT_GRID_LEVELS = 5         # Количество уровней сетки
DEFAULT_GRID_SPACING = 0.003    # Расстояние между уровнями (0.3%)

# ==================== УПРАВЛЕНИЕ РИСКАМИ ====================
MAX_DRAWDOWN_PCT = 0.05         # Максимальная просадка (5%)
STOP_LOSS_PCT = 0.02            # Стоп-лосс (2%)
MAX_API_ERRORS = 50             # Максимальное количество ошибок API

# ==================== AI ОПТИМИЗАЦИЯ ====================
AI_ANALYSIS_TIMEFRAMES = ['1', '5', '15', '60']  # Таймфреймы в минутах
VOLATILITY_LOOKBACK = 100        # Период для анализа волатильности
MIN_SESSION_DURATION = 60        # Минимальное время сессии (минуты)
MAX_SESSION_DURATION = 1440      # Максимальное время сессии (минуты) - 24 часа

# ==================== НАСТРОЙКИ ЛОГИРОВАНИЯ ====================
LOG_RETENTION_DAYS = 7          # Хранить логи за последние 7 дней

# ==================== TELEGRAM НАСТРОЙКИ ====================
TELEGRAM_POLLING_INTERVAL = 10   # Интервал проверки команд (секунды)

# Комиссии по умолчанию (будут перезаписаны из API)
DEFAULT_MAKER_FEE = 0.001  # 0.1%
DEFAULT_TAKER_FEE = 0.001  # 0.1%

# Интервал обновления комиссий (в секундах)
COMMISSION_UPDATE_INTERVAL = 3600  # 1 час
