# core/grid_bot.py
"""
🤖 ОСНОВНОЙ КЛАСС GRID TRADING BOT v9.1
"""

import time
import os
from datetime import datetime, timedelta

from config import *
from utils.api_client import APIClient
from ai.market_analyzer import MarketAnalyzer
from ai.optimizer import AIOptimizer
from telegram.bot import TelegramBot
from analytics.logger import DataLogger
from analytics.reporter import ReportGenerator
from core.risk_manager import RiskManager
from core.order_manager import OrderManager
from core.commission_tracker import CommissionTracker
from core.thread_safe import ThreadSafeManager, SafeList, AtomicCounter

class AdvancedGridBotV91:
    """🚀 ОСНОВНОЙ КЛАСС GRID TRADING BOT v9.1"""
    
    def __init__(self):
        """Инициализация бота с настройками из config.py"""
        
        # ==================== ИНИЦИАЛИЗАЦИЯ КОМПОНЕНТОВ ====================
        self.api_client = APIClient()
        self.market_analyzer = MarketAnalyzer(self.api_client)
        self.ai_optimizer = AIOptimizer(self.market_analyzer)
        self.telegram_bot = TelegramBot(self.api_client)
        self.data_logger = DataLogger()
        self.reporter = ReportGenerator(self.telegram_bot)
        self.risk_manager = RiskManager()
        self.order_manager = OrderManager(self.api_client)
        
        # ==================== НОВЫЕ МОДУЛИ v9.1 ====================
        self.commission_tracker = CommissionTracker(self.api_client)
        self.thread_safe = ThreadSafeManager()
        
        # ==================== НАСТРОЙКИ ИЗ CONFIG ====================
        self.symbol = SYMBOL
        
        # ==================== ПАРАМЕТРЫ СЕТКИ ПО УМОЛЧАНИЮ ====================
        self.grid_levels = DEFAULT_GRID_LEVELS
        self.order_size = DEFAULT_ORDER_SIZE
        self.grid_spacing = DEFAULT_GRID_SPACING
        self.monitoring_duration = 240
        self.grid_refresh_time = 1800
        
        # ==================== СТАТИСТИКА И МОНИТОРИНГ ====================
        self.total_commission = 0
        self.initial_usdt = 0
        self.initial_btc = 0
        self.total_orders_created = 0
        self.executed_orders_count = 0
        self.max_profit = 0
        self.max_drawdown = 0
        
        # ==================== ПОТОКОБЕЗОПАСНЫЕ СТРУКТУРЫ ====================
        self.active_order_ids = SafeList()
        self.order_counter = AtomicCounter()
        self.trade_log = SafeList()
        
        # ==================== СЧЕТЧИКИ ОШИБОК ====================
        self.api_errors = 0
        self.connection_retries = 0
        self.max_connection_retries = 100
        
        # ==================== ВРЕМЯ РАБОТЫ ====================
        self.start_time = None
        self.grid_count = 0
        self.last_telegram_report = 0
        self.telegram_report_interval = 1800
        
        # ==================== AI И АНАЛИТИКА ====================
        self.ai_mode = False
        self.price_history = []
        self.market_regime = "unknown"
        
        # ==================== TELEGRAM УПРАВЛЕНИЕ ====================
        self.user_commanded_stop = False
        self.user_commanded_emergency_stop = False
        
        print("✅ Бот v9.1 инициализирован с thread safety и точным учетом комиссий")

    async def initialize(self):
        """🔍 ИНИЦИАЛИЗАЦИЯ С УЧЕТОМ THREAD SAFETY"""
        print("\n🔍 Инициализация бота v9.1...")
        
        # Инициализация комиссионных ставок
        await self.commission_tracker.initialize_commission_rates([self.symbol])
        
        if not self.initialize_bot():
            print("❌ Не удалось инициализировать бота. Проверьте соединение.")
            return False
            
        return True

    def initialize_bot(self):
        """🔍 ИНИЦИАЛИЗАЦИЯ И ПРОВЕРКА СОЕДИНЕНИЯ С API BYBIT"""
        print("\n🔍 Проверка соединения с API Bybit...")
        
        price = self.api_client.get_current_price(self.symbol)
        if price is None:
            print("❌ Не удалось подключиться к API Bybit")
            return False
            
        balance = self.api_client.get_balance()
        if balance == (0, 0):
            print("❌ Не удалось получить баланс")
            return False
        
        self.initial_usdt, self.initial_btc = balance
        self.initial_price = price
            
        print(f"✅ Соединение установлено. Текущая цена: {price:.1f}")
        print(f"💰 Баланс: {balance[0]:.2f} USDT, {balance[1]:.6f} BTC")
        
        self.telegram_bot.send_start_alert({
            'usdt_balance': balance[0],
            'btc_balance': balance[1],
            'ai_mode': self.ai_mode,
            'duration': self.monitoring_duration
        })
        return True

    @ThreadSafeManager.synchronized('main_lock')
    def interactive_setup(self):
        """🎮 ИНТЕРАКТИВНАЯ НАСТРОЙКА ПАРАМЕТРОВ С THREAD SAFETY"""
        print("\n🎮 ИНТЕРАКТИВНАЯ НАСТРОЙКА AI GRID BOT v9.1")
        print("=" * 50)
        
        choice = input("\nВыберите режим:\n1. Использовать стандартные параметры\n2. Настроить параметры вручную\n3. 🤖 ПРОДВИНУТЫЙ AI-режим (рекомендуется)\n\nВаш выбор (1/2/3): ").strip()
        
        # Запрос времени работы для всех режимов
        print(f"\n⏱️ Время работы сессии (в минутах)")
        print(f"   Доступный диапазон: {MIN_SESSION_DURATION} - {MAX_SESSION_DURATION} минут")
        print(f"   Пример: 120 (2 часа), 720 (12 часов), 1440 (24 часа)")
        
        try:
            duration_input = input(f"Введите время работы (по умолчанию {self.monitoring_duration}): ").strip()
            if duration_input:
                custom_duration = int(duration_input)
                if MIN_SESSION_DURATION <= custom_duration <= MAX_SESSION_DURATION:
                    self.monitoring_duration = custom_duration
                else:
                    print(f"⚠️ Время должно быть между {MIN_SESSION_DURATION} и {MAX_SESSION_DURATION} минут. Использую значение по умолчанию.")
            else:
                print(f"✅ Использую время по умолчанию: {self.monitoring_duration} минут")
        except ValueError:
            print(f"❌ Ошибка ввода. Использую значение по умолчанию: {self.monitoring_duration} минут")
        
        if choice == "3":
            print("\n🧠 АКТИВАЦИЯ ПРОДВИНУТОГО AI-РЕЖИМА")
            print("=" * 45)
            
            if DEMO_MODE:
                print("🔸 ДЕМО-РЕЖИМ: AI использует упрощенный анализ")
                print("🔸 В реальном режиме анализ будет более точным")
            
            print("🤖 AI анализирует текущие рыночные условия...")
            
            try:
                # Получаем текущую цену для инициализации истории
                current_price = self.api_client.get_current_price(self.symbol)
                if current_price:
                    self.price_history = [current_price] * 50
                
                ai_recommendations = self.ai_optimizer.get_optimized_parameters(
                    self.price_history, 
                    self.monitoring_duration
                )
                
                print(f"📊 AI анализ завершен:")
                print(f"   📈 Режим рынка: {ai_recommendations['market_regime']}")
                print(f"   📏 Рекомендуемые уровни: {ai_recommendations['grid_levels']}")
                print(f"   🎯 Расстояние: {ai_recommendations['grid_spacing']*100:.2f}%")
                print(f"   🔄 Интервал обновления: {ai_recommendations['grid_refresh_time']} сек")
                print(f"   ⏱️ Время работы: {self.monitoring_duration} мин")
                
                if DEMO_MODE:
                    print("   💡 Примечание: В демо-режиме анализ основан на текущих данных")
                
                self.grid_levels = ai_recommendations['grid_levels']
                self.grid_spacing = ai_recommendations['grid_spacing']
                self.grid_refresh_time = ai_recommendations['grid_refresh_time']
                self.ai_mode = True
                self.market_regime = ai_recommendations['market_regime']
                
                print("✅ Параметры установлены по рекомендации AI")
                
            except Exception as e:
                print(f"❌ Ошибка AI анализа: {e}. Использую стандартные параметры.")
                self.ai_mode = True
                self.grid_levels = 4
                self.grid_spacing = 0.0015
                self.grid_refresh_time = 1800
        
        elif choice == "2":
            print("\n📊 Настройка параметров сетки:")
            
            try:
                self.grid_levels = int(input(f"Количество уровней в каждую сторону (по умолчанию {self.grid_levels}): ") or self.grid_levels)
                
                default_size = self.order_size
                size_input = input(f"Размер ордера в BTC (по умолчанию {default_size}): ") or str(default_size)
                self.order_size = float(size_input)
                
                # Используем оптимизированные минимальные расстояния
                min_distance = MIN_GRID_DISTANCES.get(self.symbol, MIN_GRID_DISTANCES["DEFAULT"])
                default_spacing = max(self.grid_spacing * 100, min_distance * 100)
                spacing_input = input(f"Расстояние между уровнями в % (минимум {min_distance*100:.2f}%, по умолчанию {default_spacing:.2f}%): ") or str(default_spacing)
                user_spacing = float(spacing_input) / 100
                
                if user_spacing < min_distance:
                    print(f"⚠️ Расстояние слишком маленькое. Установлено минимальное: {min_distance*100:.2f}%")
                    self.grid_spacing = min_distance
                else:
                    self.grid_spacing = user_spacing
                
                self.grid_refresh_time = int(input(f"Интервал пересоздания сетки в секундах (по умолчанию {self.grid_refresh_time}): ") or self.grid_refresh_time)
                
                stop_loss_input = input(f"Стоп-лосс в % (по умолчанию {STOP_LOSS_PCT * 100}%): ") or str(STOP_LOSS_PCT * 100)
                self.risk_manager.stop_loss_pct = float(stop_loss_input) / 100
                
                drawdown_input = input(f"Максимальная просадка в % (по умолчанию {MAX_DRAWDOWN_PCT * 100}%): ") or str(MAX_DRAWDOWN_PCT * 100)
                self.risk_manager.max_drawdown_pct = float(drawdown_input) / 100
                
            except ValueError as e:
                print(f"❌ Ошибка ввода: {e}. Использую значения по умолчанию.")
        
        self.print_parameters()
        
        confirm = input("\n🚀 Запустить бота с этими параметрами? (y/n): ").strip().lower()
        return confirm == 'y'

    def print_parameters(self):
        """📊 ВЫВОД ТЕКУЩИХ ПАРАМЕТРОВ БОТА"""
        print("\n📊 ТЕКУЩИЕ ПАРАМЕТРЫ БОТА v9.1:")
        print(f"   Символ: {self.symbol}")
        print(f"   Уровней сетки: {self.grid_levels} (в каждую сторону)")
        print(f"   Размер ордера: {self.order_size} BTC")
        print(f"   Расстояние между уровнями: {self.grid_spacing * 100:.2f}%")
        print(f"   Стоп-лосс: {self.risk_manager.stop_loss_pct * 100}%")
        print(f"   Макс. просадка: {self.risk_manager.max_drawdown_pct * 100}%")
        print(f"   Время работы: {self.monitoring_duration} минут ({self.monitoring_duration/60:.1f} часов)")
        print(f"   Интервал пересоздания: {self.grid_refresh_time} секунд")
        print(f"   Всего ордеров в сетке: {self.grid_levels * 2}")
        print(f"   Макс. ошибок API: {MAX_API_ERRORS}")
        print(f"   Режим: {'🤖 AI-оптимизация' if self.ai_mode else '👨‍💻 Ручной'}")
        print(f"   Thread Safety: ✅ Активен")
        print(f"   Точные комиссии: ✅ Активен")

    @ThreadSafeManager.synchronized('main_lock')
    def run_ai_enhanced_monitoring(self):
        """🔄 ОСНОВНОЙ ЦИКЛ МОНИТОРИНГА С AI ОПТИМИЗАЦИЕЙ"""
        try:
            print(f"\n🧠 Запуск AI-улучшенного мониторинга на {self.monitoring_duration} минут...")
            
            if not self.initialize_bot():
                print("❌ Не удалось инициализировать бота. Проверьте соединение.")
                return 0, True
            
            self.data_logger.setup_logging()
            
            self.initial_usdt, self.initial_btc = self.api_client.get_balance()
            self.initial_price = self.api_client.get_current_price(self.symbol)
            
            if self.initial_price is None:
                print("❌ Не удалось получить начальную цену после инициализации.")
                return 0, True
                
            initial_total_balance = self.get_total_balance_usdt()
            
            print(f"💰 Начальный баланс: {self.initial_usdt:.2f} USDT + {self.initial_btc:.6f} BTC")
            print(f"🎯 Начальная цена: {self.initial_price:.1f} USDT")
            print(f"⏰ Время начала: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"⏰ Ожидаемое время завершения: {(datetime.now() + timedelta(minutes=self.monitoring_duration)).strftime('%Y-%m-%d %H:%M:%S')}")
            
            start_time = time.time()
            end_time = start_time + (self.monitoring_duration * 60)
            self.start_time = start_time
            
            self.price_history = [self.initial_price] * 50
            
            self.executed_orders_count = 0
            self.last_telegram_report = start_time
            
            # Создаем первую сетку
            orders_placed = self.order_manager.create_grid(
                self.symbol, self.grid_levels, self.order_size, 
                self.grid_spacing, self.initial_price,
                self.commission_tracker
            )
            last_grid_time = time.time()
            self.grid_count = 1
            
            stop_triggered = False
            
            while time.time() < end_time and not stop_triggered:
                try:
                    # Проверяем команды Telegram (с защитой от старых сообщений)
                    self.telegram_bot.check_commands(self)
                    
                    if self.user_commanded_stop:
                        print("\n🛑 Получена команда остановки...")
                        stop_triggered = True
                        break
                        
                    if self.user_commanded_emergency_stop:
                        print("\n🚨 АВАРИЙНАЯ ОСТАНОВКА!")
                        self.order_manager.cancel_all_orders(self.symbol)
                        stop_triggered = True
                        break
                    
                    active_orders = self.order_manager.get_active_orders_count(self.symbol)
                    current_usdt, current_btc = self.api_client.get_balance()
                    current_price = self.api_client.get_current_price(self.symbol)
                    
                    if current_price is None:
                        print("❌ Не удалось получить текущую цену. Пропускаем итерацию...")
                        time.sleep(30)
                        continue
                    
                    # Обновляем историю цен
                    self.price_history.append(current_price)
                    if len(self.price_history) > 100:
                        self.price_history.pop(0)
                    
                    # Проверяем исполненные ордера с точным учетом комиссий
                    self.check_executed_orders(current_usdt, current_btc, current_price)
                    
                    # Расчет прибыли
                    total_balance = current_usdt + (current_btc * current_price)
                    net_profit = total_balance - initial_total_balance - self.total_commission

                    time_left = (end_time - time.time()) / 60
                    
                    # Логируем данные
                    log_data = {
                        'timestamp': datetime.now().isoformat(),
                        'current_price': current_price,
                        'active_orders': active_orders,
                        'executed_orders': self.executed_orders_count,
                        'usdt_balance': current_usdt,
                        'btc_balance': current_btc,
                        'net_profit': net_profit,
                        'total_commission': self.total_commission,
                        'grid_count': self.grid_count,
                        'time_left_min': time_left,
                        'api_errors': self.api_errors
                    }
                    self.data_logger.log_trading_data(log_data)
                    
                    print(f"\r📊 Активных: {active_orders:2d} | Исполнено: {self.executed_orders_count:2d} | Прибыль: {net_profit:+.4f} USDT | Сетка: #{self.grid_count} | Ошибки: {self.api_errors} | Осталось: {time_left:.1f} мин", end="")
                    
                    # Проверяем условия остановки
                    if self.risk_manager.check_stop_conditions(
                        net_profit, initial_total_balance, 
                        self.api_errors, self.max_profit, self.max_drawdown
                    ):
                        stop_triggered = True
                        self.telegram_bot.send_stop_alert({
                            'reason': self.risk_manager.get_stop_reason(),
                            'profit': net_profit,
                            'running_time': self.get_running_time()
                        })
                        break
                    
                    # Периодический отчет в Telegram
                    current_time = time.time()
                    if current_time - self.last_telegram_report > self.telegram_report_interval:
                        self.send_periodic_report(current_usdt, current_btc, current_price, net_profit)
                        self.last_telegram_report = current_time
                    
                    # Пересоздаем сетку по истечении времени
                    if current_time - last_grid_time > self.grid_refresh_time:
                        current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        print(f"\n🔄 [{current_timestamp}] Пересоздаём сетку (#{self.grid_count + 1})...")
                        self.order_manager.cancel_all_orders(self.symbol)
                        
                        # AI оптимизация при пересоздании сетки
                        if self.ai_mode:
                            try:
                                ai_recommendations = self.ai_optimizer.get_optimized_parameters(
                                    self.price_history, 
                                    self.monitoring_duration
                                )
                                old_levels = self.grid_levels
                                old_spacing = self.grid_spacing
                                
                                self.grid_levels = ai_recommendations['grid_levels']
                                self.grid_spacing = ai_recommendations['grid_spacing']
                                self.grid_refresh_time = ai_recommendations['grid_refresh_time']
                                
                                if old_spacing != self.grid_spacing or old_levels != self.grid_levels:
                                    print(f"🧠 AI оптимизация: уровни {old_levels}→{self.grid_levels}, расстояние {old_spacing*100:.2f}%→{self.grid_spacing*100:.2f}%")
                                    
                                    self.telegram_bot.send_ai_optimization_alert({
                                        'volatility': ai_recommendations.get('volatility', 0),
                                        'old_spacing': old_spacing,
                                        'new_spacing': self.grid_spacing,
                                        'old_levels': old_levels,
                                        'new_levels': self.grid_levels,
                                        'market_regime': ai_recommendations['market_regime']
                                    })
                                    
                            except Exception as e:
                                print(f"❌ Ошибка AI оптимизации: {e}")
                        
                        new_orders = self.order_manager.create_grid(
                            self.symbol, self.grid_levels, self.order_size, 
                            self.grid_spacing, current_price,
                            self.commission_tracker
                        )
                        last_grid_time = current_time
                        self.grid_count += 1
                    
                    time.sleep(10)
                    
                except Exception as e:
                    error_msg = f"Ошибка мониторинга: {e}"
                    print(f"\n❌ {error_msg}")
                    print("🔄 Пытаемся продолжить через 30 секунд...")
                    time.sleep(30)
            
            print(f"\n\n📈 ФИНАЛЬНЫЙ ОТЧЕТ:")
            self.order_manager.cancel_all_orders(self.symbol)
            
            final_balance = self.get_total_balance_usdt()
            total_profit = final_balance - initial_total_balance
            
            # Отправляем финальный отчет
            final_stats = {
                'initial_balance': initial_total_balance,
                'final_balance': final_balance,
                'total_profit': total_profit,
                'grid_count': self.grid_count,
                'orders_created': self.total_orders_created,
                'orders_executed': self.executed_orders_count,
                'total_commission': self.total_commission,
                'api_errors': self.api_errors,
                'running_time': self.get_running_time(),
                'market_regime': self.market_regime
            }
            
            self.reporter.send_final_report(final_stats)
            
            print(f"📊 Всего ошибок API: {self.api_errors}")
            print(f"📊 Сеток создано: {self.grid_count}")
            print(f"📦 Ордеров размещено: {self.total_orders_created}")
            print(f"✅ Ордеров исполнено: {self.executed_orders_count}")
            print(f"💸 Комиссий уплачено: {self.total_commission:.4f} USDT")
            
            return total_profit, stop_triggered
            
        except Exception as e:
            error_msg = f"Критическая ошибка в основном цикле: {e}"
            print(f"❌ {error_msg}")
            self.telegram_bot.send_error_alert({'error': error_msg})
            return 0, True

    @ThreadSafeManager.synchronized('order_lock')
    def check_executed_orders(self, current_usdt, current_btc, current_price):
        """✅ ПРОВЕРКА ИСПОЛНЕННЫХ ОРДЕРОВ С ТОЧНЫМ УЧЕТОМ КОМИССИЙ"""
        try:
            if not hasattr(self, 'last_balance_usdt'):
                self.last_balance_usdt = current_usdt
                self.last_balance_btc = current_btc
                return
            
            usdt_change = current_usdt - self.last_balance_usdt
            btc_change = current_btc - self.last_balance_btc
            
            order_threshold = self.order_size * 0.8
            if abs(btc_change) > order_threshold:
                if current_price:
                    if btc_change > 0:
                        # Точный расчет комиссии для покупки
                        commission = self.commission_tracker.calculate_commission(
                            self.symbol, btc_change, current_price, is_maker=True
                        )
                        self.total_commission += commission
                        
                        order_data = {
                            'side': 'BUY',
                            'qty': btc_change,
                            'price': current_price,
                            'commission': commission,
                            'timestamp': datetime.now().strftime('%H:%M:%S')
                        }
                        self.executed_orders_count += 1
                        self.telegram_bot.send_order_alert(order_data)
                        print(f"✅ Обнаружена покупка: {btc_change:.6f} BTC по {current_price:.1f}, комиссия: {commission:.6f} USDT")
                    
                    elif btc_change < 0:
                        # Точный расчет комиссии для продажи
                        commission = self.commission_tracker.calculate_commission(
                            self.symbol, abs(btc_change), current_price, is_maker=False
                        )
                        self.total_commission += commission
                        
                        order_data = {
                            'side': 'SELL', 
                            'qty': abs(btc_change),
                            'price': current_price,
                            'commission': commission,
                            'timestamp': datetime.now().strftime('%H:%M:%S')
                        }
                        self.executed_orders_count += 1
                        self.telegram_bot.send_order_alert(order_data)
                        print(f"✅ Обнаружена продажа: {abs(btc_change):.6f} BTC по {current_price:.1f}, комиссия: {commission:.6f} USDT")
            
            self.last_balance_usdt = current_usdt
            self.last_balance_btc = current_btc
            
        except Exception as e:
            print(f"❌ Ошибка проверки исполненных ордеров: {e}")

    @ThreadSafeManager.synchronized('main_lock')
    def get_total_balance_usdt(self):
        """💰 РАСЧЕТ ОБЩЕГО БАЛАНСА В USDT"""
        usdt, btc = self.api_client.get_balance()
        current_price = self.api_client.get_current_price(self.symbol)
        if current_price is None:
            return 0
        return usdt + (btc * current_price)

    def get_running_time(self):
        """⏰ ПОЛУЧЕНИЕ ВРЕМЕНИ РАБОТЫ БОТА"""
        if self.start_time:
            running_seconds = time.time() - self.start_time
            hours = int(running_seconds // 3600)
            minutes = int((running_seconds % 3600) // 60)
            return f"{hours:02d}:{minutes:02d}"
        return "00:00"

    @ThreadSafeManager.synchronized('main_lock')
    def send_periodic_report(self, usdt_balance, btc_balance, current_price, profit):
        """📊 ОТПРАВКА ПЕРИОДИЧЕСКОГО ОТЧЕТА"""
        try:
            total_balance = usdt_balance + (btc_balance * current_price) if current_price else 0
            
            self.telegram_bot.send_periodic_report({
                'running_time': self.get_running_time(),
                'usdt_balance': usdt_balance,
                'btc_balance': btc_balance,
                'total_balance': total_balance,
                'profit': profit,
                'commission': self.total_commission,
                'executed_orders': self.executed_orders_count,
                'grid_count': self.grid_count,
                'api_errors': self.api_errors
            })
        except Exception as e:
            print(f"❌ Ошибка отправки периодического отчета: {e}")

    @ThreadSafeManager.synchronized('main_lock')
    def send_telegram_message(self, message):
        """📨 ОТПРАВКА СООБЩЕНИЯ В TELEGRAM (для обратной совместимости)"""
        return self.telegram_bot.send_message(message)
        
    @ThreadSafeManager.synchronized('order_lock')
    def cancel_all_orders_safe(self):
        """🛑 БЕЗОПАСНАЯ ОТМЕНА ВСЕХ ОРДЕРОВ (для обратной совместимости)"""
        return self.order_manager.cancel_all_orders(self.symbol)

    @ThreadSafeManager.synchronized('main_lock')
    def get_bot_status(self):
        """📊 ПОЛУЧЕНИЕ СТАТУСА БОТА (THREAD-SAFE)"""
        return {
            'active_orders': len(self.active_order_ids),
            'is_running': not self.user_commanded_stop,
            'grid_levels': self.grid_levels,
            'executed_orders': self.executed_orders_count,
            'total_commission': self.total_commission,
            'grid_count': self.grid_count
        }
