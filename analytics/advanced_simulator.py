# analytics/advanced_simulator.py
"""
🎯 УЛУЧШЕННЫЙ СИМУЛЯТОР ТОРГОВЛИ С ТОЧНОЙ ЭМУЛЯЦИЕЙ РЕАЛЬНОГО БОТА - ВЕРСИЯ 2.0
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from tqdm import tqdm
import time
import random
import warnings
warnings.filterwarnings('ignore')

from ai.market_analyzer import MarketAnalyzer
from ai.optimizer import AIOptimizer
from core.commission_tracker import CommissionTracker
from utils.api_client import APIClient

class AdvancedTradingSimulator:
    """🎯 РЕАЛИСТИЧНЫЙ СИМУЛЯТОР С ТОЧНОЙ ЭМУЛЯЦИЕЙ GRID_BOT - ВЕРСИЯ 2.0"""
    
    def __init__(self, initial_usdt=1000, initial_btc=0.01, symbol="BTCUSDT"):
        self.initial_usdt = initial_usdt
        self.initial_btc = initial_btc
        self.symbol = symbol
        
        # Инициализация баланса
        self.current_usdt = initial_usdt
        self.current_btc = initial_btc
        self.total_commission = 0
        
        # Инициализация компонентов
        self.api_client = APIClient()
        self.market_analyzer = MarketAnalyzer(self.api_client)
        self.ai_optimizer = AIOptimizer(self.market_analyzer)
        self.commission_tracker = CommissionTracker(self.api_client, symbol)
        
        # Параметры торговли (ДОЛЖНЫ СОВПАДАТЬ С GRID_BOT)
        self.grid_levels = 5
        self.order_size_btc = 0.0002  # ТОЧНО КАК В РЕАЛЬНОМ БОТЕ
        self.grid_spacing = 0.003     # ТОЧНО КАК В РЕАЛЬНОМ БОТЕ
        self.grid_refresh_time = 1800 # 30 минут как в реальном боте
        
        # Состояние симуляции
        self.active_orders = []
        self.order_history = []
        self.grid_count = 0
        self.executed_orders_count = 0
        self.price_history = []
        
        # 🔴 НОВЫЙ АТРИБУТ: История создания сеток
        self.grid_creations = []
        
        # AI параметры (ДОЛЖНЫ СОВПАДАТЬ С РЕАЛЬНЫМ БОТОМ)
        self.ai_mode = True
        self.market_regime = "unknown"
        self.last_ai_optimization = 0
        
        # Время управления (КРИТИЧЕСКИ ВАЖНО для эмуляции)
        self.last_grid_creation = 0
        self.simulation_start_time = 0
        
        # Статистика
        self.simulation_results = []
        self.ai_decisions = []
        
        # 🔴 НОВЫЕ МЕТРИКИ: Для улучшенного анализа
        self.daily_returns = []
        self.max_drawdown = 0
        self.max_drawdown_percentage = 0
        self.peak_balance = initial_usdt + (initial_btc * 50000)  # Предполагаемая цена
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0

    def run_simulation(self, historical_data, initial_params=None):
        """
        🚀 ЗАПУСК РЕАЛИСТИЧНОЙ СИМУЛЯЦИИ С ТОЧНОЙ ЭМУЛЯЦИЕЙ - УЛУЧШЕННАЯ ВЕРСИЯ
        """
        print("🎯 ЗАПУСК ТОЧНОЙ СИМУЛЯЦИИ РЕАЛЬНОГО БОТА v2.0")
        print("=" * 50)
        
        if historical_data.empty:
            print("❌ Нет данных для симуляции")
            return []
        
        # Определяем интервал данных
        data_interval = self._detect_data_interval(historical_data)
        print(f"📊 Интервал данных: {data_interval} минут")
        
        # Устанавливаем начальные параметры
        if initial_params:
            self._set_initial_parameters(initial_params)
        
        # Инициализация времени
        self.simulation_start_time = historical_data.index[0].timestamp()
        self.last_grid_creation = self.simulation_start_time
        self.last_ai_optimization = self.simulation_start_time
        
        # Инициализация AI
        self._initialize_ai(historical_data)
        
        # Создаем первую сетку (как в реальном боте)
        first_price = historical_data['close'].iloc[0]
        self._recreate_grid(first_price, self.simulation_start_time)
        
        # Основной цикл симуляции
        results = []
        
        print(f"📊 Симуляция на {len(historical_data)} записях...")
        
        # 🔴 УЛУЧШЕНИЕ: Добавляем ежедневные метрики
        current_day = None
        daily_balances = []
        
        with tqdm(total=len(historical_data), desc="🔁 Точная симуляция v2.0") as pbar:
            for i, (timestamp, row) in enumerate(historical_data.iterrows()):
                try:
                    current_time = timestamp.timestamp()
                    current_price = row['close']
                    
                    # 🔴 УЛУЧШЕНИЕ: Ежедневные метрики
                    day_str = timestamp.strftime('%Y-%m-%d')
                    if current_day != day_str:
                        if current_day is not None:
                            # Сохраняем метрики за предыдущий день
                            if daily_balances:
                                daily_return = (daily_balances[-1] - daily_balances[0]) / daily_balances[0] * 100
                                self.daily_returns.append(daily_return)
                        current_day = day_str
                        daily_balances = []
                    
                    # Обновляем историю цен (как в реальном боте)
                    self.price_history.append(current_price)
                    if len(self.price_history) > 100:
                        self.price_history.pop(0)
                    
                    # 🔄 Пересоздание сетки по времени (как в реальном боте)
                    if self._should_recreate_grid(current_time):
                        self._recreate_grid(current_price, current_time)
                    
                    # ✅ Проверка исполнения ордеров (УЛУЧШЕННАЯ логика)
                    executed_orders = self._check_order_execution_improved(current_price, timestamp)
                    
                    # Сохранение состояния
                    state = self._capture_simulation_state(timestamp, current_price, executed_orders)
                    
                    # 🔴 УЛУЧШЕНИЕ: Расчет текущего баланса для ежедневных метрик
                    total_balance = state['total_balance_usdt']
                    daily_balances.append(total_balance)
                    
                    # 🔴 УЛУЧШЕНИЕ: Обновление максимальной просадки
                    self._update_drawdown_metrics(total_balance)
                    
                    results.append(state)
                    
                    # Обновление прогресс-бара
                    pbar.update(1)
                    if len(results) % 100 == 0:
                        pbar.set_postfix({
                            'Прибыль': f"{state['total_profit_usdt']:+.2f}",
                            'Ордеров': state['executed_orders'],
                            'Сетки': state['grid_count'],
                            'Просадка': f"{self.max_drawdown_percentage:.1f}%"
                        })
                        
                except Exception as e:
                    print(f"⚠️ Ошибка в симуляции: {e}")
                    continue
        
        # 🔴 УЛУЧШЕНИЕ: Финализация ежедневных метрик
        if daily_balances:
            daily_return = (daily_balances[-1] - daily_balances[0]) / daily_balances[0] * 100
            self.daily_returns.append(daily_return)
        
        self.simulation_results = results
        print("✅ Точная симуляция завершена")
        return results

    def _update_drawdown_metrics(self, current_balance):
        """📉 ОБНОВЛЕНИЕ МЕТРИК МАКСИМАЛЬНОЙ ПРОСАДКИ"""
        if current_balance > self.peak_balance:
            self.peak_balance = current_balance
        
        drawdown = self.peak_balance - current_balance
        if drawdown > self.max_drawdown:
            self.max_drawdown = drawdown
            self.max_drawdown_percentage = (drawdown / self.peak_balance) * 100 if self.peak_balance > 0 else 0

    def _check_order_execution_improved(self, current_price, timestamp):
        """✅ ПРОВЕРКА ИСПОЛНЕНИЯ ОРДЕРОВ (УЛУЧШЕННАЯ ЛОГИКА С РЕАЛИЗМОМ)"""
        executed_orders = []
        
        for order in self.active_orders[:]:  # Используем копию для безопасного удаления
            is_executed = False
            
            # 🔴 УЛУЧШЕНИЕ: Добавляем реализм - ордер исполняется не мгновенно
            # 1. Проверяем, достигнута ли цена ордера
            # 2. Добавляем вероятность исполнения в зависимости от ликвидности
            # 3. Учитываем частичное исполнение
            
            if order['type'] == 'buy' and current_price <= order['price']:
                # Для покупки: цена ниже или равна цене ордера
                execution_probability = self._calculate_execution_probability(order, current_price, 'buy')
                if random.random() < execution_probability:
                    is_executed = self._execute_buy_order(order, current_price, timestamp)
                    
            elif order['type'] == 'sell' and current_price >= order['price']:
                # Для продажи: цена выше или равна цене ордера
                execution_probability = self._calculate_execution_probability(order, current_price, 'sell')
                if random.random() < execution_probability:
                    is_executed = self._execute_sell_order(order, current_price, timestamp)
            
            if is_executed:
                executed_orders.append(order)
                self.active_orders.remove(order)
                
                # 🔴 УЛУЧШЕНИЕ: Обновляем статистику сделок
                self.total_trades += 1
                if order['type'] == 'sell':
                    # Для sell ордеров считаем прибыль
                    buy_price = self._find_matching_buy_price(order)
                    if buy_price > 0:
                        profit_pct = ((order['price'] - buy_price) / buy_price) * 100
                        if profit_pct > 0:
                            self.winning_trades += 1
                        else:
                            self.losing_trades += 1
        
        return executed_orders

    def _calculate_execution_probability(self, order, current_price, order_type):
        """🎲 РАСЧЕТ ВЕРОЯТНОСТИ ИСПОЛНЕНИЯ ОРДЕРА С УЧЕТОМ РЕАЛИЗМА"""
        # Базовую вероятность устанавливаем в 95%
        base_probability = 0.95
        
        # Корректируем в зависимости от типа ордера и цены
        if order_type == 'buy':
            # Для buy: чем дальше цена от ордера, тем выше вероятность
            price_diff_pct = abs(current_price - order['price']) / order['price']
            probability = base_probability + min(0.04, price_diff_pct * 10)
        else:  # sell
            # Для sell: аналогично
            price_diff_pct = abs(current_price - order['price']) / order['price']
            probability = base_probability + min(0.04, price_diff_pct * 10)
        
        # Ограничиваем вероятность от 90% до 99%
        return max(0.90, min(0.99, probability))

    def _find_matching_buy_price(self, sell_order):
        """🔍 ПОИСК ЦЕНЫ ПОКУПКИ ДЛЯ ПРОДАЖИ (для расчета P&L)"""
        # Ищем последнюю покупку с похожим количеством
        for order in reversed(self.order_history):
            if order['type'] == 'buy' and abs(order['quantity'] - sell_order['quantity']) < 0.00001:
                return order['price']
        return 0

    def _detect_data_interval(self, historical_data):
        """🔍 ОПРЕДЕЛЕНИЕ ИНТЕРВАЛА ДАННЫХ"""
        if len(historical_data) < 2:
            return 5  # По умолчанию
        
        # Вычисляем разницу между первыми двумя временными метками
        time_diff = historical_data.index[1] - historical_data.index[0]
        interval_minutes = time_diff.total_seconds() / 60
        
        # Округляем до ближайшего стандартного интервала
        standard_intervals = [1, 3, 5, 15, 60]
        closest = min(standard_intervals, key=lambda x: abs(x - interval_minutes))
        
        return closest

    def _should_recreate_grid(self, current_time):
        """🔄 ПРОВЕРКА ПЕРЕСОЗДАНИЯ СЕТКИ (ТОЧНАЯ ЭМУЛЯЦИЯ РЕАЛЬНОГО БОТА)"""
        # В реальном боте сетка пересоздается каждые grid_refresh_time секунд
        time_since_last_grid = current_time - self.last_grid_creation
        return time_since_last_grid >= self.grid_refresh_time

    def _recreate_grid(self, current_price, current_time):
        """📊 ПЕРЕСОЗДАНИЕ СЕТКИ (ТОЧНАЯ ЭМУЛЯЦИЯ РЕАЛЬНОГО БОТА)"""
        # Отменяем все активные ордера (как в реальном боте)
        self.active_orders = []
        
        # 🔴 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: AI оптимизация выполняется ПРИ ПЕРЕСОЗДАНИИ СЕТКИ
        # (как в реальном боте)
        if self.ai_mode:
            self._perform_ai_optimization(current_time)
        
        # Рассчитываем цены для сетки (ТОЧНО КАК В ORDER_MANAGER)
        buy_prices, sell_prices = self._calculate_grid_prices(current_price)
        
        # Создаем ордера на покупку (с проверкой баланса)
        buy_orders_created = self._create_buy_orders(buy_prices)
        
        # Создаем ордера на продажу (с проверкой баланса)  
        sell_orders_created = self._create_sell_orders(sell_prices)
        
        total_orders = buy_orders_created + sell_orders_created
        
        if total_orders > 0:
            # 🔴 СОХРАНЯЕМ ИНФОРМАЦИЮ О СОЗДАНИИ СЕТКИ
            grid_info = {
                'timestamp': current_time,
                'grid_count': self.grid_count + 1,
                'grid_levels': self.grid_levels,
                'grid_spacing': self.grid_spacing,
                'grid_refresh_time': self.grid_refresh_time,
                'market_regime': self.market_regime,
                'current_price': current_price,
                'orders_created': total_orders,
                'ai_optimized': self.ai_mode  # 🔴 ВСЕГДА True если AI режим включен
            }
            self.grid_creations.append(grid_info)
            
            self.grid_count += 1
            self.last_grid_creation = current_time
            
        return total_orders

    def _calculate_grid_prices(self, current_price):
        """🎯 РАСЧЕТ ЦЕН ДЛЯ СЕТКИ (ТОЧНО КАК В РЕАЛЬНОМ БОТЕ)"""
        buy_prices = []
        sell_prices = []
        
        for i in range(1, self.grid_levels + 1):
            # Цены покупки (ниже текущей) - ТОЧНО КАК В ORDER_MANAGER
            buy_price = round(current_price * (1 - i * self.grid_spacing), 1)
            if buy_price > 0:
                buy_prices.append(buy_price)
            
            # Цены продажи (выше текущей) - ТОЧНО КАК В ORDER_MANAGER
            sell_price = round(current_price * (1 + i * self.grid_spacing), 1)
            sell_prices.append(sell_price)
        
        return buy_prices, sell_prices

    def _create_buy_orders(self, buy_prices):
        """📥 СОЗДАНИЕ ОРДЕРОВ НА ПОКУПКУ (С ПРОВЕРКОЙ БАЛАНСА)"""
        orders_created = 0
        
        for price in buy_prices:
            order_cost = self.order_size_btc * price
            commission = self.commission_tracker.calculate_maker_commission(
                self.order_size_btc, price
            )
            total_cost = order_cost + commission
            
            # Проверяем достаточно ли USDT (с запасом 10% на комиссии)
            if self.current_usdt >= total_cost * 1.1:
                self.active_orders.append({
                    'type': 'buy',
                    'price': price,
                    'quantity': self.order_size_btc,
                    'created_at': time.time()
                })
                orders_created += 1
        
        return orders_created

    def _create_sell_orders(self, sell_prices):
        """📤 СОЗДАНИЕ ОРДЕРОВ НА ПРОДАЖУ (С ПРОВЕРКОЙ БАЛАНСА)"""
        orders_created = 0
        
        for price in sell_prices:
            # Проверяем достаточно ли BTC
            if self.current_btc >= self.order_size_btc:
                self.active_orders.append({
                    'type': 'sell', 
                    'price': price,
                    'quantity': self.order_size_btc,
                    'created_at': time.time()
                })
                orders_created += 1
        
        return orders_created

    def _execute_buy_order(self, order, current_price, timestamp):
        """🟢 ИСПОЛНЕНИЕ ОРДЕРА НА ПОКУПКУ (С КОМИССИЯМИ)"""
        try:
            cost = order['quantity'] * order['price']
            commission = self.commission_tracker.calculate_taker_commission(
                order['quantity'], order['price']
            )
            total_cost = cost + commission
            
            if self.current_usdt >= total_cost:
                self.current_usdt -= total_cost
                self.current_btc += order['quantity']
                self.total_commission += commission
                self.executed_orders_count += 1
                
                # Сохраняем в историю
                self.order_history.append({
                    'timestamp': timestamp,
                    'type': 'buy',
                    'price': order['price'],
                    'quantity': order['quantity'],
                    'commission': commission,
                    'current_price': current_price
                })
                
                return True
            
            return False
        except Exception as e:
            print(f"⚠️ Ошибка исполнения BUY ордера: {e}")
            return False

    def _execute_sell_order(self, order, current_price, timestamp):
        """🔴 ИСПОЛНЕНИЕ ОРДЕРА НА ПРОДАЖУ (С КОМИССИЯМИ)"""
        try:
            if self.current_btc >= order['quantity']:
                revenue = order['quantity'] * order['price']
                commission = self.commission_tracker.calculate_taker_commission(
                    order['quantity'], order['price']
                )
                net_revenue = revenue - commission
                
                self.current_btc -= order['quantity']
                self.current_usdt += net_revenue
                self.total_commission += commission
                self.executed_orders_count += 1
                
                # Сохраняем в историю
                self.order_history.append({
                    'timestamp': timestamp,
                    'type': 'sell', 
                    'price': order['price'],
                    'quantity': order['quantity'],
                    'commission': commission,
                    'current_price': current_price
                })
                
                return True
            
            return False
        except Exception as e:
            print(f"⚠️ Ошибка исполнения SELL ордера: {e}")
            return False

    def _perform_ai_optimization(self, current_time):
        """🧠 AI ОПТИМИЗАЦИЯ (РАБОЧАЯ ВЕРСИЯ) - ТОЧНО КАК В РЕАЛЬНОМ БОТЕ"""
        try:
            if not self.ai_mode:
                return
                
            old_levels = self.grid_levels
            old_spacing = self.grid_spacing
            old_refresh = self.grid_refresh_time
            
            print(f"🧠 Запуск AI оптимизации на времени {current_time}...")
            
            # Проверяем достаточно ли данных для анализа
            if len(self.price_history) < 50:
                print("⚠️ Недостаточно данных для AI оптимизации")
                return
                
            # 🔴 ВАЖНО: Используем ТОЧНО ТАКУЮ ЖЕ ЛОГИКУ КАК В РЕАЛЬНОМ БОТЕ
            ai_params = self.ai_optimizer.get_optimized_parameters(
                self.price_history, 1440  # 24 часа
            )
            
            # Сохраняем старые параметры для сравнения
            changed = False
            
            if self.grid_levels != ai_params['grid_levels']:
                changed = True
            if abs(self.grid_spacing - ai_params['grid_spacing']) > 0.0001:
                changed = True
            if self.grid_refresh_time != ai_params['grid_refresh_time']:
                changed = True
            
            # Обновляем параметры
            self.grid_levels = ai_params['grid_levels']
            self.grid_spacing = ai_params['grid_spacing']
            self.grid_refresh_time = ai_params['grid_refresh_time']
            self.market_regime = ai_params['market_regime']
            self.last_ai_optimization = current_time
            
            # Логируем решение AI только если параметры изменились
            if changed:
                decision = {
                    'timestamp': current_time,
                    'old_levels': old_levels,
                    'new_levels': self.grid_levels,
                    'old_spacing': old_spacing,
                    'new_spacing': self.grid_spacing,
                    'old_refresh': old_refresh,
                    'new_refresh': self.grid_refresh_time,
                    'market_regime': self.market_regime,
                    'volatility': ai_params.get('volatility', 0)
                }
                self.ai_decisions.append(decision)
                
                print(f"🧠 AI оптимизация: уровни {old_levels}→{self.grid_levels}, "
                      f"расстояние {old_spacing*100:.3f}%→{self.grid_spacing*100:.3f}%, "
                      f"режим: {self.market_regime}")
            else:
                print(f"🧠 AI анализ: параметры оптимальны, режим: {self.market_regime}")
                      
        except Exception as e:
            print(f"⚠️ Ошибка AI оптимизации: {e}")
            import traceback
            print(f"Детали: {traceback.format_exc()}")

    def _initialize_ai(self, historical_data):
        """🤖 ИНИЦИАЛИЗАЦИЯ AI С ИСТОРИЧЕСКИМИ ДАННЫМИ"""
        print("🧠 Инициализация AI для симуляции...")
        
        # Используем первые 100 точек для инициализации истории цен
        initial_prices = historical_data['close'].head(100).tolist()
        self.price_history = initial_prices
        
        if self.ai_mode:
            try:
                ai_params = self.ai_optimizer.get_optimized_parameters(
                    self.price_history, 1440
                )
                self.grid_levels = ai_params['grid_levels']
                self.grid_spacing = ai_params['grid_spacing']
                self.grid_refresh_time = ai_params['grid_refresh_time']
                self.market_regime = ai_params['market_regime']
                
                print(f"✅ AI инициализирован для симуляции: {self.grid_levels} уровней, "
                      f"{self.grid_spacing*100:.3f}%, режим {self.market_regime}")
                      
            except Exception as e:
                print(f"⚠️ Ошибка инициализации AI: {e}")

    def _set_initial_parameters(self, params):
        """⚙️ УСТАНОВКА НАЧАЛЬНЫХ ПАРАМЕТРОВ"""
        self.grid_levels = params.get('grid_levels', self.grid_levels)
        self.order_size_btc = params.get('order_size_btc', self.order_size_btc)
        self.grid_spacing = params.get('grid_spacing', self.grid_spacing)
        self.grid_refresh_time = params.get('grid_refresh_time', self.grid_refresh_time)
        self.ai_mode = params.get('ai_mode', self.ai_mode)

    def _capture_simulation_state(self, timestamp, current_price, executed_orders):
        """📊 ЗАХВАТ ТЕКУЩЕГО СОСТОЯНИЯ СИМУЛЯЦИИ"""
        total_balance_usdt = self.current_usdt + (self.current_btc * current_price)
        initial_total = self.initial_usdt + (self.initial_btc * current_price)
        total_profit_usdt = total_balance_usdt - initial_total - self.total_commission
        
        # 🔴 УЛУЧШЕНИЕ: Добавляем расчет ROI
        roi_percentage = (total_profit_usdt / initial_total) * 100 if initial_total > 0 else 0
        
        return {
            'timestamp': timestamp,
            'current_price': current_price,
            'total_balance_usdt': total_balance_usdt,
            'total_profit_usdt': total_profit_usdt,
            'roi_percentage': roi_percentage,
            'usdt_balance': self.current_usdt,
            'btc_balance': self.current_btc,
            'active_orders': len(self.active_orders),
            'executed_orders': self.executed_orders_count,
            'grid_count': self.grid_count,
            'total_commission': self.total_commission,
            'market_regime': self.market_regime,
            'grid_levels': self.grid_levels,
            'grid_spacing': self.grid_spacing,
            'grid_refresh_time': self.grid_refresh_time
        }

    def get_simulation_statistics(self):
        """📈 СТАТИСТИКА СИМУЛЯЦИИ"""
        if not self.simulation_results:
            return {
                'initial_usdt': self.initial_usdt,
                'initial_btc': self.initial_btc,
                'final_balance': self.initial_usdt + (self.initial_btc * 0),
                'total_profit': 0,
                'total_orders': 0,
                'grid_count': 0,
                'total_commission': 0,
                'ai_optimizations': 0
            }
            
        last_state = self.simulation_results[-1]
        
        # 🔴 УЛУЧШЕНИЕ: Добавляем продвинутые метрики
        stats = {
            'initial_usdt': self.initial_usdt,
            'initial_btc': self.initial_btc,
            'final_balance': last_state['total_balance_usdt'],
            'total_profit': last_state['total_profit_usdt'],
            'roi_percentage': last_state.get('roi_percentage', 0),
            'total_orders': self.executed_orders_count,
            'grid_count': self.grid_count,
            'total_commission': self.total_commission,
            'ai_optimizations': len(self.ai_decisions),
            'max_drawdown': self.max_drawdown,
            'max_drawdown_percentage': self.max_drawdown_percentage,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0,
            'profit_per_trade': (last_state['total_profit_usdt'] / self.total_trades) if self.total_trades > 0 else 0
        }
        
        # 🔴 УЛУЧШЕНИЕ: Расчет Sharpe Ratio если есть ежедневные доходности
        if len(self.daily_returns) > 1:
            daily_returns_array = np.array(self.daily_returns)
            if np.std(daily_returns_array) > 0:
                stats['sharpe_ratio'] = (np.mean(daily_returns_array) / np.std(daily_returns_array)) * np.sqrt(365)
            else:
                stats['sharpe_ratio'] = 0
            stats['daily_returns_std'] = np.std(daily_returns_array)
            stats['avg_daily_return'] = np.mean(daily_returns_array)
        
        return stats
