"""
Grid Trading Bot v9.1 - ПОЛНОСТЬЮ ПЕРЕРАБОТАННЫЙ КОД
"""

import logging
import threading
import time
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

from core.order_manager import OrderManager
from core.risk_manager import RiskManager
from core.commission_tracker import CommissionTracker
from core.thread_safe import synchronized, SafeList, AtomicCounter
from utils.bybit_client import BybitClient
from analytics.performance_tracker import PerformanceTracker


class GridTradingBot:
    """Основной класс Grid Trading Bot с полными исправлениями"""
    
    def __init__(self, config, symbol: str = None, grid_levels: int = None, 
                 lower_bound: float = None, upper_bound: float = None):
        self.config = config
        self.symbol = symbol or config.SYMBOL
        self.grid_levels = grid_levels or config.DEFAULT_GRID_LEVELS
        self.lower_bound = Decimal(str(lower_bound)) if lower_bound else None
        self.upper_bound = Decimal(str(upper_bound)) if upper_bound else None
        
        # Инициализация компонентов
        self.bybit_client = BybitClient(
            api_key=config.BYBIT_API_KEY,
            api_secret=config.BYBIT_API_SECRET,
            demo_mode=config.DEMO_MODE,
            testnet=getattr(config, 'BYBIT_TESTNET', True)
        )
        
        self.order_manager = OrderManager(self.bybit_client, config)
        self.risk_manager = RiskManager(config)
        self.performance_tracker = PerformanceTracker()
        self.commission_tracker = CommissionTracker(self.bybit_client)
        
        # Thread-safe структуры данных
        self._operation_lock = threading.RLock()
        self.active_orders = SafeList()
        self.order_history = SafeList()
        self.trade_count = AtomicCounter()
        self.is_running = False
        
        # Состояние бота
        self.grid_prices = []
        self.current_price = Decimal('0')
        self.balance = Decimal('0')
        self.equity = Decimal('0')
        self.session_start_time = datetime.now()
        
        self.logger = logging.getLogger(__name__)
        self._initialize_bot()
    
    def _initialize_bot(self):
        """Инициализация бота"""
        try:
            # Получение текущей цены и баланса
            self.current_price = self._get_current_price()
            self.balance = self._get_account_balance()
            
            # Расчет границ сетки, если не заданы
            if not self.lower_bound or not self.upper_bound:
                self._calculate_grid_bounds()
            
            # Создание уровней сетки
            self._create_grid_levels()
            
            # Обновление комиссий через API
            self.commission_tracker.update_fee_rates(self.symbol)
            
            self.logger.info(f"Grid Bot инициализирован для {self.symbol}")
            self.logger.info(f"Уровни: {self.grid_levels}, Границы: {self.lower_bound}-{self.upper_bound}")
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации бота: {e}")
            raise
    
    @synchronized
    def start(self):
        """Запуск торгового бота"""
        if self.is_running:
            self.logger.warning("Бот уже запущен")
            return
        
        self.is_running = True
        self.session_start_time = datetime.now()
        self.logger.info("Запуск Grid Trading Bot...")
        
        try:
            # Отмена всех активных ордеров перед началом
            self._cancel_all_orders()
            
            # Размещение начальных ордеров
            self._place_initial_orders()
            
            # Запуск основного цикла в отдельном потоке
            self._start_main_loop()
            
        except Exception as e:
            self.logger.error(f"Ошибка при запуске бота: {e}")
            self.stop()
    
    def _start_main_loop(self):
        """Запуск основного цикла в отдельном потоке"""
        def run_loop():
            while self.is_running:
                try:
                    self._main_loop_iteration()
                    time.sleep(1)  # Пауза между итерациями
                except Exception as e:
                    self.logger.error(f"Ошибка в основном цикле: {e}")
                    time.sleep(5)
        
        self.main_loop_thread = threading.Thread(target=run_loop, daemon=True)
        self.main_loop_thread.start()
    
    def _main_loop_iteration(self):
        """Одна итерация основного цикла"""
        # Обновление текущей цены
        self.current_price = self._get_current_price()
        
        # Проверка исполнения ордеров
        self._check_order_fills()
        
        # Проверка рисков
        if not self.risk_manager.check_risk_limits(self.equity, self.balance):
            self.logger.warning("Превышены лимиты рисков - остановка")
            self.stop()
            return
        
        # Перерасчет сетки при значительном движении цены
        self._check_grid_recalculation()
        
        # Обновление производительности
        self._update_performance()
    
    @synchronized
    def _place_initial_orders(self):
        """Размещение начальных ордеров сетки"""
        self.logger.info("Размещение начальных ордеров сетки...")
        
        for price in self.grid_prices:
            if price < self.current_price:
                # Ордера на покупку ниже текущей цены
                self._create_buy_order(price)
            else:
                # Ордера на продажу выше текущей цены
                self._create_sell_order(price)
    
    @synchronized
    def _create_buy_order(self, price: Decimal):
        """Создание ордера на покупку"""
        try:
            quantity = Decimal(str(self.config.DEFAULT_ORDER_SIZE))
            
            # Создание ордера
            order_result = self.order_manager.create_limit_buy_order(
                symbol=self.symbol,
                quantity=float(quantity),
                price=float(price)
            )
            
            if order_result:
                # Расчет комиссии
                commission = self.order_manager.calculate_order_commission(
                    order_type="BUY",
                    quantity=float(quantity),
                    price=float(price),
                    is_maker=True
                )
                
                # Запись комиссии
                self.commission_tracker.record_commission(
                    order_id=order_result['orderId'],
                    symbol=self.symbol,
                    commission=commission,
                    order_type="BUY",
                    timestamp=datetime.now()
                )
                
                # Сохранение ордера
                order_data = {
                    'order_id': order_result['orderId'],
                    'symbol': self.symbol,
                    'side': 'BUY',
                    'price': price,
                    'quantity': quantity,
                    'timestamp': datetime.now(),
                    'commission': commission
                }
                
                self.active_orders.append(order_data)
                self.trade_count.increment()
                
                self.logger.info(f"Создан BUY ордер: {quantity} {self.symbol} по {price}")
                
                return order_result
            else:
                self.logger.error("Не удалось создать BUY ордер")
                return None
                
        except Exception as e:
            self.logger.error(f"Ошибка создания BUY ордера: {e}")
            return None
    
    @synchronized
    def _create_sell_order(self, price: Decimal):
        """Создание ордера на продажу"""
        try:
            quantity = Decimal(str(self.config.DEFAULT_ORDER_SIZE))
            
            # Создание ордера
            order_result = self.order_manager.create_limit_sell_order(
                symbol=self.symbol,
                quantity=float(quantity),
                price=float(price)
            )
            
            if order_result:
                # Расчет комиссии
                commission = self.order_manager.calculate_order_commission(
                    order_type="SELL",
                    quantity=float(quantity),
                    price=float(price),
                    is_maker=True
                )
                
                # Запись комиссии
                self.commission_tracker.record_commission(
                    order_id=order_result['orderId'],
                    symbol=self.symbol,
                    commission=commission,
                    order_type="SELL",
                    timestamp=datetime.now()
                )
                
                # Сохранение ордера
                order_data = {
                    'order_id': order_result['orderId'],
                    'symbol': self.symbol,
                    'side': 'SELL',
                    'price': price,
                    'quantity': quantity,
                    'timestamp': datetime.now(),
                    'commission': commission
                }
                
                self.active_orders.append(order_data)
                self.trade_count.increment()
                
                self.logger.info(f"Создан SELL ордер: {quantity} {self.symbol} по {price}")
                
                return order_result
            else:
                self.logger.error("Не удалось создать SELL ордер")
                return None
                
        except Exception as e:
            self.logger.error(f"Ошибка создания SELL ордера: {e}")
            return None
    
    def _get_current_price(self) -> Decimal:
        """Получение текущей цены"""
        try:
            ticker = self.bybit_client.get_ticker(symbol=self.symbol)
            return Decimal(str(ticker['lastPrice']))
        except Exception as e:
            self.logger.error(f"Ошибка получения цены: {e}")
            return Decimal('0')
    
    def _get_account_balance(self) -> Decimal:
        """Получение баланса аккаунта"""
        try:
            balance_info = self.bybit_client.get_wallet_balance()
            return Decimal(str(balance_info['totalEquity']))
        except Exception as e:
            self.logger.error(f"Ошибка получения баланса: {e}")
            return Decimal('0')
    
    def _calculate_grid_bounds(self):
        """Расчет границ сетки на основе текущей цены"""
        volatility_factor = Decimal('0.05')  # 5% волатильность
        
        self.lower_bound = self.current_price * (Decimal('1') - volatility_factor)
        self.upper_bound = self.current_price * (Decimal('1') + volatility_factor)
        
        self.logger.info(f"Рассчитаны границы сетки: {self.lower_bound} - {self.upper_bound}")
    
    def _create_grid_levels(self):
        """Создание уровней цен для сетки"""
        price_range = self.upper_bound - self.lower_bound
        step = price_range / (self.grid_levels - 1)
        
        self.grid_prices = [
            self.lower_bound + step * i 
            for i in range(self.grid_levels)
        ]
        
        self.logger.info(f"Создано {len(self.grid_prices)} уровней сетки")
    
    @synchronized
    def _check_order_fills(self):
        """Проверка исполнения ордеров"""
        orders_to_remove = []
        
        for order in self.active_orders.copy():
            try:
                order_status = self.order_manager.get_order_status(
                    symbol=self.symbol,
                    order_id=order['order_id']
                )
                
                if order_status == 'FILLED':
                    self._handle_filled_order(order)
                    orders_to_remove.append(order)
                    
            except Exception as e:
                self.logger.error(f"Ошибка проверки ордера {order['order_id']}: {e}")
        
        # Удаляем исполненные ордера
        for order in orders_to_remove:
            if order in self.active_orders:
                self.active_orders.remove(order)
    
    @synchronized
    def _handle_filled_order(self, order: Dict):
        """Обработка исполненного ордера"""
        try:
            # Перемещение в историю
            order['filled_time'] = datetime.now()
            self.order_history.append(order)
            
            # Создание противоположного ордера
            if order['side'] == 'BUY':
                new_price = order['price'] * Decimal('1.005')  # +0.5% для прибыли
                self._create_sell_order(new_price)
                self.logger.info(f"BUY ордер исполнен, создан SELL ордер по {new_price}")
            else:
                new_price = order['price'] * Decimal('0.995')   # -0.5% для покупки
                self._create_buy_order(new_price)
                self.logger.info(f"SELL ордер исполнен, создан BUY ордер по {new_price}")
            
        except Exception as e:
            self.logger.error(f"Ошибка обработки исполненного ордера: {e}")
    
    @synchronized
    def _cancel_all_orders(self):
        """Отмена всех активных ордеров"""
        try:
            for order in self.active_orders:
                self.order_manager.cancel_order(
                    symbol=self.symbol,
                    order_id=order['order_id']
                )
            
            self.active_orders.clear()
            self.logger.info("Все активные ордера отменены")
            
        except Exception as e:
            self.logger.error(f"Ошибка отмены ордеров: {e}")
    
    def _check_grid_recalculation(self):
        """Проверка необходимости перерасчета сетки"""
        # Если цена вышла за пределы текущей сетки на 10%, пересчитываем
        price_change_threshold = Decimal('0.10')
        
        if (self.current_price < self.lower_bound * (Decimal('1') - price_change_threshold) or
            self.current_price > self.upper_bound * (Decimal('1') + price_change_threshold)):
            
            self.logger.info("Цена значительно изменилась, пересчитываем сетку...")
            self._recalculate_grid()
    
    @synchronized
    def _recalculate_grid(self):
        """Перерасчет сетки"""
        try:
            # Отмена текущих ордеров
            self._cancel_all_orders()
            
            # Перерасчет границ
            self._calculate_grid_bounds()
            self._create_grid_levels()
            
            # Размещение новых ордеров
            self._place_initial_orders()
            
            self.logger.info("Сетка успешно пересчитана")
            
        except Exception as e:
            self.logger.error(f"Ошибка перерасчета сетки: {e}")
    
    def _update_performance(self):
        """Обновление метрик производительности"""
        try:
            self.equity = self.balance + self._calculate_unrealized_pnl()
            self.performance_tracker.update_metrics(
                equity=float(self.equity),
                balance=float(self.balance),
                active_orders=len(self.active_orders),
                total_trades=self.trade_count.get()
            )
        except Exception as e:
            self.logger.error(f"Ошибка обновления производительности: {e}")
    
    def _calculate_unrealized_pnl(self) -> Decimal:
        """Расчет нереализованного PnL"""
        # Упрощенный расчет - в реальной реализации нужно учитывать позиции
        try:
            total_commission = Decimal(str(self.commission_tracker.get_total_commissions()))
            return -total_commission  # Пока только комиссии
        except:
            return Decimal('0')
    
    def _save_state(self):
        """Сохранение состояния бота"""
        try:
            # TODO: Реализовать сохранение состояния в файл/БД
            pass
        except Exception as e:
            self.logger.error(f"Ошибка сохранения состояния: {e}")
    
    @synchronized
    def stop(self):
        """Остановка бота"""
        self.is_running = False
        self.logger.info("Остановка Grid Trading Bot...")
        
        try:
            self._cancel_all_orders()
            self._save_state()
            
            # Отчет о сессии
            session_duration = datetime.now() - self.session_start_time
            self.logger.info(f"Сессия завершена. Длительность: {session_duration}")
            
        except Exception as e:
            self.logger.error(f"Ошибка при остановке бота: {e}")
    
    def get_status(self) -> Dict:
        """Получение статуса бота"""
        try:
            total_commissions = self.commission_tracker.get_total_commissions()
            
            return {
                'symbol': self.symbol,
                'is_running': self.is_running,
                'current_price': float(self.current_price),
                'balance': float(self.balance),
                'equity': float(self.equity),
                'active_orders': len(self.active_orders),
                'total_trades': self.trade_count.get(),
                'total_commissions': float(total_commissions),
                'grid_levels': self.grid_levels,
                'grid_bounds': {
                    'lower': float(self.lower_bound),
                    'upper': float(self.upper_bound)
                },
                'session_duration': str(datetime.now() - self.session_start_time)
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {}
