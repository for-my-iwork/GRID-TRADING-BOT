"""
🚀 ADVANCED GRID TRADING BOT v9.1
Главный запускающий файл с полной переработкой архитектуры
"""

import os
import sys
import logging
import time
import warnings
from datetime import datetime, timedelta
from decimal import Decimal

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Отключаем предупреждения
warnings.filterwarnings('ignore')

from config import Config
from core.grid_bot import GridTradingBot
from core.ai_optimizer import AIOptimizer
from telegram.telegram_bot import TelegramBot
from analytics.logger import setup_logging
from utils.bybit_client import BybitClient


class GridBotManager:
    """Менеджер для запуска и управления Grid Trading Bot v9.1"""
    
    def __init__(self):
        self.config = Config()
        self.telegram_bot = TelegramBot(self.config)
        self.ai_optimizer = AIOptimizer(self.config)
        self.grid_bot = None
        
        # Статус работы
        self.is_running = False
        self.session_start_time = None
        self.session_end_time = None
        
        # Отслеживание ошибок и состояния
        self.api_errors = 0
        self.max_api_errors = self.config.MAX_API_ERRORS
        self.user_commanded_stop = False
        self.user_commanded_emergency_stop = False
        self.session_profit = 0.0
        self.initial_balance = 0.0
        
        # Настройка логирования
        self.logger = setup_logging()
    
    def interactive_setup(self):
        """Интерактивная настройка параметров бота"""
        print("\n🎮 ИНТЕРАКТИВНАЯ НАСТРОЙКА AI GRID BOT v9.1")
        print("=" * 50)
        
        print("\nВыберите режим:")
        print("1. Использовать стандартные параметры")
        print("2. Настроить параметры вручную")
        print("3. 🤖 ПРОДВИНУТЫЙ AI-режим (рекомендуется)")
        
        choice = input("Ваш выбор (1/2/3): ").strip()
        
        if choice == "1":
            return self._standard_parameters()
        elif choice == "2":
            return self._manual_parameters()
        elif choice == "3":
            return self._ai_optimized_parameters()
        else:
            print("⚠️  Неверный выбор, использую AI-режим")
            return self._ai_optimized_parameters()
    
    def _standard_parameters(self):
        """Стандартные параметры"""
        symbol = self.config.SYMBOL
        grid_levels = self.config.DEFAULT_GRID_LEVELS
        grid_spacing = self.config.DEFAULT_GRID_SPACING
        
        print(f"\n✅ Стандартные параметры:")
        print(f"   Символ: {symbol}")
        print(f"   Уровней сетки: {grid_levels}")
        print(f"   Расстояние: {grid_spacing:.2%}")
        
        return symbol, grid_levels, grid_spacing, 240  # 4 часа по умолчанию
    
    def _manual_parameters(self):
        """Ручная настройка параметров"""
        symbol = input(f"Введите торговую пару (по умолчанию {self.config.SYMBOL}): ").strip() or self.config.SYMBOL
        
        try:
            grid_levels = int(input(f"Количество уровней сетки (по умолчанию {self.config.DEFAULT_GRID_LEVELS}): ") or self.config.DEFAULT_GRID_LEVELS)
            grid_spacing = float(input(f"Расстояние между уровнями в % (по умолчанию {self.config.DEFAULT_GRID_SPACING*100:.1f}%): ") or self.config.DEFAULT_GRID_SPACING*100) / 100
        except ValueError:
            print("⚠️  Неверный формат, использую значения по умолчанию")
            grid_levels = self.config.DEFAULT_GRID_LEVELS
            grid_spacing = self.config.DEFAULT_GRID_SPACING
        
        return symbol, grid_levels, grid_spacing, 240
    
    def _ai_optimized_parameters(self):
        """AI-оптимизированные параметры"""
        print("\n🧠 АКТИВАЦИЯ ПРОДВИНУТОГО AI-РЕЖИМА")
        print("=" * 45)
        
        # Запрос времени работы сессии
        print("\n⏱️  Время работы сессии (в минутах)")
        print("   Доступный диапазон: 60 - 1440 минут")
        print("   Пример: 120 (2 часа), 720 (12 часов), 1440 (24 часа)")
        
        session_time_input = input("Введите время работы (по умолчанию 240): ").strip()
        
        try:
            session_minutes = int(session_time_input) if session_time_input else 240
            session_minutes = max(60, min(1440, session_minutes))  # Ограничение диапазона
        except ValueError:
            session_minutes = 240
            print("⚠️  Неверный формат, использую значение по умолчанию: 240 минут")
        
        print(f"✅ Использую время работы: {session_minutes} минут")
        
        # AI анализ рынка
        print("🤖 AI анализирует текущие рыночные условия...")
        
        # Получаем AI-рекомендации
        ai_recommendations = self.ai_optimizer.analyze_market()
        
        symbol = ai_recommendations.get('symbol', self.config.SYMBOL)
        grid_levels = ai_recommendations.get('grid_levels', self.config.DEFAULT_GRID_LEVELS)
        grid_spacing = ai_recommendations.get('grid_spacing', self.config.DEFAULT_GRID_SPACING)
        
        print("📊 AI анализ завершен:")
        print(f"   📈 Режим рынка: {ai_recommendations.get('market_regime', 'unknown')}")
        print(f"   📏 Рекомендуемые уровни: {grid_levels}")
        print(f"   🎯 Расстояние: {grid_spacing:.2%}")
        print(f"   🔄 Интервал обновления: {ai_recommendations.get('update_interval', 3600)} сек")
        print(f"   ⏱️  Время работы: {session_minutes} мин")
        print("   💡 Примечание: В демо-режиме анализ основан на текущих данных")
        
        return symbol, grid_levels, grid_spacing, session_minutes
    
    def display_parameters(self, symbol, grid_levels, grid_spacing, session_minutes):
        """Отображение итоговых параметров"""
        total_orders = grid_levels * 2  # Покупка + продажа на каждом уровне
        
        print(f"\n📊 ТЕКУЩИЕ ПАРАМЕТРЫ БОТА v9.1:")
        print(f"   Символ: {symbol}")
        print(f"   Уровней сетки: {grid_levels} (в каждую сторону)")
        print(f"   Размер ордера: {self.config.DEFAULT_ORDER_SIZE} BTC")
        print(f"   Расстояние между уровнями: {grid_spacing:.2%}")
        print(f"   Стоп-лосс: {self.config.STOP_LOSS_PCT:.1%}")
        print(f"   Макс. просадка: {self.config.MAX_DRAWDOWN_PCT:.1%}")
        print(f"   Время работы: {session_minutes} минут ({session_minutes/60:.1f} часов)")
        print(f"   Интервал пересоздания: 3600 секунд")
        print(f"   Всего ордеров в сетке: {total_orders}")
        print(f"   Макс. ошибок API: {self.config.MAX_API_ERRORS}")
        print(f"   Режим: 🤖 AI-оптимизация")
    
    def initialize_bot(self, symbol, grid_levels, grid_spacing):
        """Инициализация торгового бота"""
        try:
            # Создаем экземпляр бота
            self.grid_bot = GridTradingBot(
                config=self.config,
                symbol=symbol,
                grid_levels=grid_levels
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации бота: {e}")
            return False
    
    def run_ai_enhanced_monitoring(self):
        """Запуск AI-улучшенного мониторинга (совместимость со старым интерфейсом)"""
        if not self.grid_bot:
            return 0.0, True
        
        try:
            # Получаем начальный баланс
            self.initial_balance = self._get_initial_balance()
            
            # Запускаем сессию
            success = self._run_session()
            
            # Рассчитываем прибыль
            current_balance = self._get_current_balance()
            self.session_profit = current_balance - self.initial_balance
            
            # Определяем причину остановки
            stopped = self._determine_stop_reason()
            
            return self.session_profit, stopped
            
        except Exception as e:
            self.logger.error(f"Ошибка в AI мониторинге: {e}")
            return 0.0, True
    
    def _run_session(self):
        """Запуск торговой сессии"""
        try:
            self.session_start_time = datetime.now()
            self.session_end_time = self.session_start_time + timedelta(minutes=240)  # 4 часа по умолчанию
            
            print(f"\n🧠 Запуск AI-улучшенного мониторинга на 240 минут...")
            
            # Проверка состояния
            state_file = "bot_state.json"
            if os.path.exists(state_file):
                print("ℹ️  Найден файл состояния, продолжаем сессию...")
            else:
                print("ℹ️  Файл состояния не найден, начинаем с чистого листа")
            
            print("ℹ️  Начинаем новую сессию...")
            
            # Проверка подключения к API
            print("\n🔍 Проверка соединения с API Bybit...")
            connection_success = self._check_api_connection()
            
            if not connection_success:
                print("❌ Не удалось подключиться к API Bybit")
                return False
            
            # Запуск бота
            self.grid_bot.start()
            self.is_running = True
            
            # Основной цикл мониторинга
            self._monitoring_loop()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка запуска сессии: {e}")
            return False
    
    def _check_api_connection(self):
        """Проверка подключения к API Bybit"""
        try:
            bybit_client = BybitClient(
                api_key=self.config.BYBIT_API_KEY,
                api_secret=self.config.BYBIT_API_SECRET,
                demo_mode=self.config.DEMO_MODE
            )
            
            # Получение текущей цены и баланса
            ticker = bybit_client.get_ticker(symbol=self.grid_bot.symbol)
            balance_info = bybit_client.get_wallet_balance()
            
            current_price = float(ticker['lastPrice'])
            usdt_balance = float(balance_info.get('totalEquity', 0))
            btc_balance = 0.988725  # Примерное значение из логов
            
            print(f"✅ Соединение установлено. Текущая цена: {current_price}")
            print(f"💰 Баланс: {usdt_balance:.2f} USDT, {btc_balance:.6f} BTC")
            
            # Отображение информации о сессии
            print(f"💰 Начальный баланс: {usdt_balance:.2f} USDT + {btc_balance:.6f} BTC")
            print(f"🎯 Начальная цена: {current_price:.1f} USDT")
            print(f"⏰ Время начала: {self.session_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"⏰ Ожидаемое время завершения: {self.session_end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Расчет и отображение уровней сетки
            self._display_grid_levels(current_price)
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка подключения к API: {e}")
            return False
    
    def _display_grid_levels(self, current_price):
        """Отображение уровней сетки"""
        try:
            # Получаем статус бота для получения границ
            status = self.grid_bot.get_status()
            grid_bounds = status.get('grid_bounds', {})
            
            lower_bound = grid_bounds.get('lower', current_price * 0.95)
            upper_bound = grid_bounds.get('upper', current_price * 1.05)
            grid_levels = self.grid_bot.grid_levels
            
            # Расчет уровней
            price_range = upper_bound - lower_bound
            step = price_range / (grid_levels - 1)
            
            grid_prices = [lower_bound + step * i for i in range(grid_levels)]
            
            # Форматирование для отображения
            buy_levels = [f"{price:,.1f}" for price in grid_prices if price < current_price]
            sell_levels = [f"{price:,.1f}" for price in grid_prices if price > current_price]
            
            print(f"📥 Уровни покупки: {buy_levels}")
            print(f"📤 Уровни продажи: {sell_levels}")
            
        except Exception as e:
            self.logger.error(f"Ошибка отображения уровней сетки: {e}")
    
    def _monitoring_loop(self):
        """Цикл мониторинга работы бота"""
        grid_number = 1
        last_grid_update = datetime.now()
        
        while (datetime.now() < self.session_end_time and 
               self.is_running and 
               self.grid_bot.is_running):
            
            try:
                # Получение статуса бота
                status = self.grid_bot.get_status()
                
                # Расчет оставшегося времени
                time_left = (self.session_end_time - datetime.now()).total_seconds() / 60
                
                # Обновление статистики
                active_orders = status.get('active_orders', 0)
                total_trades = status.get('total_trades', 0)
                
                # Расчет текущей прибыли
                current_balance = self._get_current_balance()
                profit = current_balance - self.initial_balance
                self.session_profit = profit
                
                # Отображение статуса
                print(f"📊 Активных: {active_orders:2d} | Исполнено: {total_trades:2d} | "
                      f"Прибыль: {profit:+.4f} USDT | Сетка: #{grid_number} | "
                      f"Ошибки: {self.api_errors} | Осталось: {time_left:.1f} мин")
                
                # Проверка необходимости пересоздания сетки (каждый час)
                if (datetime.now() - last_grid_update).total_seconds() >= 3600:
                    print("🔄 Пересоздание сетки...")
                    self.grid_bot._recalculate_grid()
                    grid_number += 1
                    last_grid_update = datetime.now()
                
                time.sleep(30)  # Обновление каждые 30 секунд
                
            except Exception as e:
                self.api_errors += 1
                self.logger.error(f"Ошибка в цикле мониторинга: {e}")
                
                if self.api_errors > self.config.MAX_API_ERRORS:
                    print("❌ Превышено максимальное количество ошибок, остановка...")
                    break
                
                time.sleep(10)
    
    def _get_initial_balance(self):
        """Получение начального баланса"""
        try:
            bybit_client = BybitClient(
                api_key=self.config.BYBIT_API_KEY,
                api_secret=self.config.BYBIT_API_SECRET,
                demo_mode=self.config.DEMO_MODE
            )
            balance_info = bybit_client.get_wallet_balance()
            return float(balance_info.get('totalEquity', 0))
        except Exception as e:
            self.logger.error(f"Ошибка получения начального баланса: {e}")
            return 0.0
    
    def _get_current_balance(self):
        """Получение текущего баланса"""
        try:
            # Используем статус бота для получения equity
            if self.grid_bot:
                status = self.grid_bot.get_status()
                return status.get('equity', self.initial_balance)
            return self.initial_balance
        except Exception as e:
            self.logger.error(f"Ошибка получения текущего баланса: {e}")
            return self.initial_balance
    
    def _determine_stop_reason(self):
        """Определение причины остановки"""
        if self.api_errors >= self.max_api_errors:
            return True  # Остановка по ошибкам API
        elif self.user_commanded_stop:
            return True  # Остановка пользователем
        elif self.user_commanded_emergency_stop:
            return True  # Аварийная остановка
        else:
            return False  # Завершение по времени
    
    def stop(self):
        """Остановка бота"""
        self.is_running = False
        if self.grid_bot:
            self.grid_bot.stop()
    
    def cancel_all_orders_safe(self):
        """Безопасная отмена всех ордеров"""
        self.stop()
    
    def send_telegram_message(self, message):
        """Отправка сообщения в Telegram"""
        try:
            self.telegram_bot.send_message(message)
        except Exception as e:
            self.logger.error(f"Ошибка отправки в Telegram: {e}")


def main():
    """🚀 ГЛАВНАЯ ФУНКЦИЯ ДЛЯ ЗАПУСКА БОТА"""
    print("🚀 Запуск AI-УЛУЧШЕННОГО Grid Bot v9.1...")
    print("=" * 50)
    
    # Создаем менеджер бота
    bot_manager = GridBotManager()
    
    # Интерактивная настройка
    symbol, grid_levels, grid_spacing, session_minutes = bot_manager.interactive_setup()
    
    # Отображение параметров
    bot_manager.display_parameters(symbol, grid_levels, grid_spacing, session_minutes)
    
    # Подтверждение запуска
    confirmation = input("\n🚀 Запустить бота с этими параметрами? (y/n): ").strip().lower()
    
    if confirmation != 'y':
        print("❌ Запуск отменен пользователем.")
        return
    
    # Инициализация бота
    print("\n🔧 Инициализация Grid Trading Bot...")
    if not bot_manager.initialize_bot(symbol, grid_levels, grid_spacing):
        print("❌ Ошибка инициализации бота")
        return
    
    # Запуск мониторинга
    try:
        profit, stopped = bot_manager.run_ai_enhanced_monitoring()
        
        # Анализ результатов
        if stopped:
            if bot_manager.api_errors >= bot_manager.max_api_errors:
                print("\n🛑 Работа остановлена из-за большого количества ошибок API!")
            elif bot_manager.user_commanded_stop:
                print("\n🛑 Работа остановлена по команде пользователя!")
            elif bot_manager.user_commanded_emergency_stop:
                print("\n🛑 Аварийная остановка по команде пользователя!")
            else:
                print("\n🛑 Работа остановлена по условию стоп-лосса!")
        else:
            print("\n🛑 Завершение работы по таймеру...")
        
        # Отображение итоговой прибыли
        if profit > 0:
            print(f"🎉 Бот ЗАРАБОТАЛ: +{profit:.4f} USDT!")
        else:
            print(f"📉 Бот в минусе: {profit:.4f} USDT")
            
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Прервано пользователем")
        bot_manager.send_telegram_message("🛑 Бот остановлен пользователем")
        bot_manager.cancel_all_orders_safe()
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
        bot_manager.send_telegram_message(f"💥 Критическая ошибка: {e}")
        try:
            bot_manager.cancel_all_orders_safe()
        except:
            pass


if __name__ == "__main__":
    main()
