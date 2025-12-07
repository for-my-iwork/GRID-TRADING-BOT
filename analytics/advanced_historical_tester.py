# analytics/advanced_historical_tester.py
"""
🎯 УЛУЧШЕННЫЙ ИСТОРИЧЕСКИЙ ТЕСТЕР С ТОЧНОЙ ЭМУЛЯЦИЕЙ - ВЕРСИЯ 2.0
"""

from analytics.data_loader import HistoricalDataLoader
from analytics.advanced_simulator import AdvancedTradingSimulator
from analytics.reporter import ReportGenerator
from core.commission_tracker import CommissionTracker
from utils.api_client import APIClient
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class AdvancedHistoricalTester:
    """🎯 ТЕСТЕР С ТОЧНОЙ ЭМУЛЯЦИЕЙ РЕАЛЬНОГО БОТА - ВЕРСИЯ 2.0"""
    
    def __init__(self):
        self.data_loader = HistoricalDataLoader()
        self.simulator = None
        self.reporter = ReportGenerator()

    def run_complete_test(self, days=30, initial_balance=1000, initial_btc=0.01, 
                         ai_mode=True, force_reload=False):
        """
        🚀 ПОЛНЫЙ ЦИКЛ ТЕСТИРОВАНИЯ С ТОЧНОЙ ЭМУЛЯЦИЕЙ - УЛУЧШЕННАЯ ВЕРСИЯ
        """
        print("🎯 ЗАПУСК ТОЧНОГО ТЕСТИРОВАНИЯ РЕАЛЬНОГО БОТА v2.0")
        print("=" * 60)
        
        # ЭТАП 1: Загрузка данных с меньшим интервалом для точности
        print("📥 ЭТАП 1: Загрузка исторических данных...")
        historical_data = self.data_loader.load_and_save_data(
            days=days, interval="1", force_reload=force_reload  # 1-минутные данные для точности
        )
        
        if historical_data.empty:
            print("❌ Не удалось загрузить данные")
            return {}
        
        # 🔴 УЛУЧШЕНИЕ: Проверяем качество данных
        print(f"📊 Проверка данных: {len(historical_data)} записей")
        print(f"📅 Период: {historical_data.index[0]} - {historical_data.index[-1]}")
        print(f"💰 Диапазон цен: {historical_data['close'].min():.1f} - {historical_data['close'].max():.1f}")
        
        # ЭТАП 2: Запуск точной симуляции
        print("\n🔁 ЭТАП 2: Запуск точной торговой симуляции...")
        self.simulator = AdvancedTradingSimulator(
            initial_usdt=initial_balance,
            initial_btc=initial_btc,
            symbol="BTCUSDT"
        )
        self.simulator.ai_mode = ai_mode
        
        # Устанавливаем параметры как в реальном боте
        simulation_results = self.simulator.run_simulation(historical_data)
        
        # Проверяем результаты
        if not simulation_results:
            print("❌ Симуляция не дала результатов")
            return {}
        
        # ЭТАП 3: Детальный анализ результатов
        print("\n📊 ЭТАП 3: Детальный анализ результатов...")
        analysis = self.analyze_results_advanced(simulation_results, historical_data)
        
        # ЭТАП 4: Генерация точного отчета
        print("\n📄 ЭТАП 4: Генерация точного отчета...")
        self.generate_comprehensive_report(analysis, days)
        
        # 🔴 УЛУЧШЕНИЕ: Сохранение детализированных данных
        print("\n💾 ЭТАП 5: Сохранение детализированных данных...")
        self.save_detailed_data(analysis, days)
        
        # 🔴 НОВЫЙ ЭТАП: Сохранение полных результатов для анализа
        print("\n📁 ЭТАП 6: Сохранение полных результатов...")
        self.save_complete_results(analysis, days)
        
        return analysis

    def analyze_results_advanced(self, simulation_results, historical_data):
        """📈 РАСШИРЕННЫЙ АНАЛИЗ РЕЗУЛЬТАТОВ С УЛУЧШЕННЫМИ МЕТРИКАМИ"""
        if not simulation_results:
            print("⚠️ Нет данных для анализа")
            return self._get_empty_analysis()
        
        df = pd.DataFrame(simulation_results)
        df.set_index('timestamp', inplace=True)
        
        stats = self.simulator.get_simulation_statistics()
        
        # Точный расчет прибыли
        initial_total = self.simulator.initial_usdt + (self.simulator.initial_btc * historical_data['close'].iloc[0])
        final_total = stats.get('final_balance', initial_total)
        total_profit = stats.get('total_profit', 0)
        profit_percentage = (total_profit / initial_total) * 100 if initial_total > 0 else 0
        
        # Сравнение с HODL
        hodl_profit = self.calculate_hodl_performance_advanced(historical_data, initial_total)
        
        # 🔴 УЛУЧШЕНИЕ: Расчет дополнительных метрик
        # 1. Sharpe Ratio
        sharpe_ratio = stats.get('sharpe_ratio', 0)
        
        # 2. Максимальная просадка
        max_drawdown = stats.get('max_drawdown', 0)
        max_drawdown_pct = stats.get('max_drawdown_percentage', 0)
        
        # 3. Статистика сделок
        win_rate = stats.get('win_rate', 0)
        profit_per_trade = stats.get('profit_per_trade', 0)
        
        # 4. Волатильность доходности
        daily_returns_std = stats.get('daily_returns_std', 0)
        avg_daily_return = stats.get('avg_daily_return', 0)
        
        # 5. Коэффициент восстановления
        recovery_factor = total_profit / max_drawdown if max_drawdown > 0 else 0
        
        # 6. Коэффициент Сортино (учитывает только негативную волатильность)
        sortino_ratio = self.calculate_sortino_ratio(stats, avg_daily_return, daily_returns_std)
        
        # Детальная аналитика
        analysis = {
            'summary': {
                'initial_balance': initial_total,
                'final_balance': final_total,
                'total_profit': total_profit,
                'total_profit_percentage': profit_percentage,
                'hodl_profit': hodl_profit,
                'vs_hodl': total_profit - hodl_profit,
                'total_orders': stats.get('total_orders', 0),
                'grid_count': stats.get('grid_count', 0),
                'total_commission': stats.get('total_commission', 0),
                'ai_optimizations': stats.get('ai_optimizations', 0),
                'execution_efficiency': self.calculate_execution_efficiency(stats)
            },
            'advanced_metrics': {
                'sharpe_ratio': sharpe_ratio,
                'sortino_ratio': sortino_ratio,
                'max_drawdown': max_drawdown,
                'max_drawdown_percentage': max_drawdown_pct,
                'recovery_factor': recovery_factor,
                'win_rate': win_rate,
                'total_trades': stats.get('total_trades', 0),
                'winning_trades': stats.get('winning_trades', 0),
                'losing_trades': stats.get('losing_trades', 0),
                'profit_per_trade': profit_per_trade,
                'daily_returns_std': daily_returns_std,
                'avg_daily_return': avg_daily_return,
                'volatility_ratio': daily_returns_std / abs(avg_daily_return) if avg_daily_return != 0 else 0
            },
            'final_balances': {
                'usdt': self.simulator.current_usdt,
                'btc': self.simulator.current_btc,
                'last_price': historical_data['close'].iloc[-1] if not historical_data.empty else 0
            },
            'simulation_data': df,
            'order_history': self.simulator.order_history,
            'ai_decisions': self.simulator.ai_decisions,
            'grid_creations': self.simulator.grid_creations,
            'parameters': {
                'initial_usdt': self.simulator.initial_usdt,
                'initial_btc': self.simulator.initial_btc,
                'ai_mode': self.simulator.ai_mode,
                'grid_levels': self.simulator.grid_levels,
                'grid_spacing': self.simulator.grid_spacing,
                'grid_refresh_time': self.simulator.grid_refresh_time
            }
        }
        
        # Вывод расширенной статистики
        self._print_advanced_statistics(analysis)
        
        return analysis

    def calculate_sortino_ratio(self, stats, avg_return, total_std):
        """📊 РАСЧЕТ КОЭФФИЦИЕНТА СОРТИНО"""
        if 'daily_returns' in stats and len(stats['daily_returns']) > 0:
            daily_returns = np.array(stats['daily_returns'])
            negative_returns = daily_returns[daily_returns < 0]
            if len(negative_returns) > 0:
                downside_std = np.std(negative_returns)
                if downside_std > 0:
                    return (avg_return / downside_std) * np.sqrt(365)
        return 0

    def calculate_hodl_performance_advanced(self, historical_data, initial_balance):
        """📈 РАСЧЕТ ДОХОДНОСТИ СТРАТЕГИИ HODL С УЧЕТОМ КОМИССИЙ"""
        if historical_data.empty:
            return 0
            
        initial_price = historical_data['close'].iloc[0]
        final_price = historical_data['close'].iloc[-1]
        
        # Предполагаем, что мы покупаем весь баланс в BTC в начале
        initial_btc = initial_balance / initial_price
        
        # Учитываем комиссии на вход и выход (примерно как в симуляторе)
        commission_tracker = CommissionTracker(APIClient(), "BTCUSDT")
        buy_commission = commission_tracker.calculate_taker_commission(initial_btc, initial_price)
        sell_commission = commission_tracker.calculate_taker_commission(initial_btc, final_price)
        total_commission = buy_commission + sell_commission
        
        hodl_value = (initial_btc * final_price) - total_commission
        
        return hodl_value - initial_balance

    def _print_advanced_statistics(self, analysis):
        """📋 ВЫВОД РАСШИРЕННОЙ СТАТИСТИКИ"""
        summary = analysis['summary']
        advanced = analysis['advanced_metrics']
        params = analysis['parameters']
        final_balances = analysis['final_balances']
        
        print("\n📊 РАСШИРЕННАЯ СТАТИСТИКА ТЕСТИРОВАНИЯ:")
        print(f"   📈 Прибыль: {summary['total_profit']:+.2f} USDT ({summary['total_profit_percentage']:+.2f}%)")
        print(f"   🎯 VS HODL: {summary['vs_hodl']:+.2f} USDT")
        print(f"   📉 Макс. просадка: {advanced['max_drawdown']:.2f} USDT ({advanced['max_drawdown_percentage']:.1f}%)")
        print(f"   📊 Sharpe Ratio: {advanced['sharpe_ratio']:.2f}")
        print(f"   📊 Sortino Ratio: {advanced['sortino_ratio']:.2f}")
        print(f"   🎯 Win Rate: {advanced['win_rate']:.1f}% ({advanced['winning_trades']}/{advanced['total_trades']})")
        print(f"   📈 Прибыль на сделку: {advanced['profit_per_trade']:.4f} USDT")
        print(f"   💰 Финальный баланс USDT: {final_balances['usdt']:.2f}")
        print(f"   ₿ Финальный баланс BTC: {final_balances['btc']:.6f}")
        print(f"   💵 Последний курс BTC: {final_balances['last_price']:.2f} USDT")
        print(f"   🔄 Сделок: {summary['total_orders']}")
        print(f"   📊 Сеток: {summary['grid_count']}")
        print(f"   💸 Комиссии: {summary['total_commission']:.4f} USDT")
        print(f"   🧠 AI оптимизаций: {summary['ai_optimizations']}")
        print(f"   ⚡ Эффективность: {summary['execution_efficiency']:.1f}%")
        print(f"   ⚙️ Параметры: {params['grid_levels']} ур., {params['grid_spacing']*100:.2f}%")

    def calculate_execution_efficiency(self, stats):
        """📊 РАСЧЕТ ЭФФЕКТИВНОСТИ ИСПОЛНЕНИЯ"""
        total_orders = stats.get('total_orders', 0)
        grid_count = stats.get('grid_count', 0)
        
        if grid_count == 0:
            return 0
            
        expected_orders = grid_count * stats.get('grid_levels', 5) * 2  * 0.3  # 30% эффективность
        if expected_orders == 0:
            return 0
            
        return min(100, (total_orders / expected_orders) * 100)

    def _get_empty_analysis(self):
        """🔄 ВОЗВРАТ ПУСТОГО АНАЛИЗА ПРИ ОШИБКАХ"""
        return {
            'summary': {
                'initial_balance': 0,
                'final_balance': 0,
                'total_profit': 0,
                'total_profit_percentage': 0,
                'hodl_profit': 0,
                'vs_hodl': 0,
                'total_orders': 0,
                'grid_count': 0,
                'total_commission': 0,
                'ai_optimizations': 0,
                'execution_efficiency': 0
            },
            'advanced_metrics': {
                'sharpe_ratio': 0,
                'sortino_ratio': 0,
                'max_drawdown': 0,
                'max_drawdown_percentage': 0,
                'recovery_factor': 0,
                'win_rate': 0,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'profit_per_trade': 0,
                'daily_returns_std': 0,
                'avg_daily_return': 0,
                'volatility_ratio': 0
            },
            'final_balances': {
                'usdt': 0,
                'btc': 0,
                'last_price': 0
            },
            'simulation_data': pd.DataFrame(),
            'order_history': [],
            'ai_decisions': [],
            'grid_creations': [],
            'parameters': {}
        }

    def save_detailed_data(self, analysis, days):
        """💾 СОХРАНЕНИЕ ДЕТАЛИЗИРОВАННЫХ ДАННЫХ В CSV ФАЙЛЫ"""
        try:
            timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_filename = f"detailed_backtest_data_{days}days_{timestamp_str}"
            
            # 🔴 ФАЙЛ 1: Исполненные ордера
            if analysis['order_history']:
                orders_data = []
                for order in analysis['order_history']:
                    orders_data.append({
                        'timestamp': order['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                        'type': order['type'].upper(),
                        'price': order['price'],
                        'quantity_btc': order['quantity'],
                        'quantity_usdt': order['price'] * order['quantity'],
                        'commission_usdt': order['commission'],
                        'current_price_at_execution': order.get('current_price', 0)
                    })
                
                orders_df = pd.DataFrame(orders_data)
                orders_filename = f"{base_filename}_orders.csv"
                orders_df.to_csv(orders_filename, index=False, encoding='utf-8')
                print(f"✅ Сохранено {len(orders_df)} исполненных ордеров в: {orders_filename}")
            else:
                print("ℹ️ Нет данных об исполненных ордерах")
            
            # 🔴 ФАЙЛ 2: Созданные сетки
            if analysis.get('grid_creations'):
                grids_data = []
                for grid in analysis['grid_creations']:
                    grids_data.append({
                        'timestamp': datetime.fromtimestamp(grid['timestamp']).strftime('%Y-%m-%d %H:%M:%S'),
                        'grid_number': grid['grid_count'],
                        'grid_levels': grid['grid_levels'],
                        'grid_spacing_percent': grid['grid_spacing'] * 100,
                        'grid_refresh_time_seconds': grid['grid_refresh_time'],
                        'market_regime': grid['market_regime'],
                        'current_price_at_creation': grid['current_price'],
                        'orders_created': grid.get('orders_created', 0),
                        'ai_optimized': grid.get('ai_optimized', False)
                    })
                
                grids_df = pd.DataFrame(grids_data)
                grids_filename = f"{base_filename}_grids.csv"
                grids_df.to_csv(grids_filename, index=False, encoding='utf-8')
                print(f"✅ Сохранено {len(grids_df)} созданных сеток в: {grids_filename}")
            else:
                print("ℹ️ Нет данных о созданных сетках")
            
            # 🔴 ФАЙЛ 3: AI оптимизации
            if analysis['ai_decisions']:
                ai_data = []
                for decision in analysis['ai_decisions']:
                    ai_data.append({
                        'timestamp': datetime.fromtimestamp(decision['timestamp']).strftime('%Y-%m-%d %H:%M:%S'),
                        'old_levels': decision['old_levels'],
                        'new_levels': decision['new_levels'],
                        'old_spacing_percent': decision['old_spacing'] * 100,
                        'new_spacing_percent': decision['new_spacing'] * 100,
                        'market_regime': decision['market_regime'],
                        'volatility': decision.get('volatility', 0)
                    })
                
                ai_df = pd.DataFrame(ai_data)
                ai_filename = f"{base_filename}_ai_optimizations.csv"
                ai_df.to_csv(ai_filename, index=False, encoding='utf-8')
                print(f"✅ Сохранено {len(ai_df)} AI оптимизаций в: {ai_filename}")
            else:
                print("ℹ️ Нет данных об AI оптимизациях")
            
            # 🔴 ФАЙЛ 4: Детализированные метрики
            metrics_data = {
                'basic_metrics': analysis['summary'],
                'advanced_metrics': analysis['advanced_metrics']
            }
            
            # Сохраняем как JSON для удобства
            metrics_filename = f"{base_filename}_metrics.json"
            import json
            with open(metrics_filename, 'w', encoding='utf-8') as f:
                json.dump(metrics_data, f, indent=2, ensure_ascii=False, default=str)
            print(f"✅ Сохранены метрики в: {metrics_filename}")
            
            print(f"💾 Все детализированные данные сохранены с префиксом: {base_filename}")
            
        except Exception as e:
            print(f"❌ Ошибка сохранения детализированных данных: {e}")
            import traceback
            print(f"Детали ошибки: {traceback.format_exc()}")

    def save_complete_results(self, analysis, days):
        """📁 СОХРАНЕНИЕ ПОЛНЫХ РЕЗУЛЬТАТОВ СИМУЛЯЦИИ"""
        try:
            timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"complete_simulation_results_{days}days_{timestamp_str}.csv"
            
            if not analysis['simulation_data'].empty:
                # Сохраняем все данные симуляции
                simulation_df = analysis['simulation_data'].copy()
                simulation_df.to_csv(filename, encoding='utf-8')
                print(f"✅ Полные результаты симуляции сохранены в: {filename}")
                
                # Также сохраняем сводку
                summary_filename = f"simulation_summary_{days}days_{timestamp_str}.txt"
                with open(summary_filename, 'w', encoding='utf-8') as f:
                    f.write("=" * 60 + "\n")
                    f.write("ПОЛНАЯ СВОДКА СИМУЛЯЦИИ GRID BOT\n")
                    f.write("=" * 60 + "\n\n")
                    
                    summary = analysis['summary']
                    advanced = analysis['advanced_metrics']
                    
                    f.write("ОСНОВНЫЕ МЕТРИКИ:\n")
                    f.write(f"  Прибыль: {summary['total_profit']:+.2f} USDT ({summary['total_profit_percentage']:+.2f}%)\n")
                    f.write(f"  VS HODL: {summary['vs_hodl']:+.2f} USDT\n")
                    f.write(f"  Сделок: {summary['total_orders']}\n")
                    f.write(f"  Сеток: {summary['grid_count']}\n")
                    f.write(f"  Комиссии: {summary['total_commission']:.4f} USDT\n\n")
                    
                    f.write("РАСШИРЕННЫЕ МЕТРИКИ:\n")
                    f.write(f"  Sharpe Ratio: {advanced['sharpe_ratio']:.2f}\n")
                    f.write(f"  Sortino Ratio: {advanced['sortino_ratio']:.2f}\n")
                    f.write(f"  Макс. просадка: {advanced['max_drawdown_percentage']:.1f}%\n")
                    f.write(f"  Win Rate: {advanced['win_rate']:.1f}%\n")
                    f.write(f"  Коэф. восстановления: {advanced['recovery_factor']:.2f}\n\n")
                    
                    f.write("ПАРАМЕТРЫ ТЕСТИРОВАНИЯ:\n")
                    f.write(f"  Дней: {days}\n")
                    f.write(f"  Режим: {'AI' if analysis['parameters']['ai_mode'] else 'Ручной'}\n")
                    f.write(f"  Уровни сетки: {analysis['parameters']['grid_levels']}\n")
                    f.write(f"  Расстояние: {analysis['parameters']['grid_spacing']*100:.2f}%\n")
                    
                print(f"✅ Сводка сохранена в: {summary_filename}")
                
        except Exception as e:
            print(f"❌ Ошибка сохранения полных результатов: {e}")

    def generate_comprehensive_report(self, analysis, days):
        """📄 ГЕНЕРАЦИЯ КОМПЛЕКСНОГО ОТЧЕТА С ГРАФИКАМИ"""
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"advanced_backtest_report_{days}days_{timestamp_str}.html"
        
        # Создаем визуализации
        if not analysis['simulation_data'].empty:
            self.create_advanced_charts(analysis)
        
        # Генерируем HTML отчет
        html_content = self._generate_advanced_html_report(analysis, days, timestamp_str)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Расширенный отчет сохранен: {filename}")
        
        # Также сохраняем краткий текстовый отчет
        self._save_text_report(analysis, days, timestamp_str)

    def create_advanced_charts(self, analysis):
        """📊 СОЗДАНИЕ РАСШИРЕННЫХ ГРАФИКОВ"""
        try:
            df = analysis['simulation_data']
            
            plt.style.use('seaborn-v0_8-darkgrid')
            fig, axes = plt.subplots(3, 2, figsize=(16, 18))
            fig.suptitle('Расширенный анализ симуляции Grid Bot', fontsize=16, fontweight='bold')
            
            # 1. Баланс и прибыль
            axes[0, 0].plot(df.index, df['total_balance_usdt'], label='Общий баланс', color='blue', linewidth=2)
            axes[0, 0].plot(df.index, df['total_profit_usdt'] + analysis['parameters']['initial_usdt'], 
                           label='Прибыль', color='green', linestyle='--', linewidth=2)
            axes[0, 0].set_title('Динамика баланса и прибыли', fontsize=12, fontweight='bold')
            axes[0, 0].legend()
            axes[0, 0].grid(True, alpha=0.3)
            axes[0, 0].set_ylabel('USDT', fontsize=10)
            
            # 2. Активность ордеров
            if analysis['order_history']:
                orders_df = pd.DataFrame(analysis['order_history'])
                buy_orders = orders_df[orders_df['type'] == 'buy']
                sell_orders = orders_df[orders_df['type'] == 'sell']
                
                if not buy_orders.empty:
                    axes[0, 1].scatter(buy_orders['timestamp'], buy_orders['price'], 
                                     color='green', marker='^', label='Покупки', s=50, alpha=0.7)
                if not sell_orders.empty:
                    axes[0, 1].scatter(sell_orders['timestamp'], sell_orders['price'],
                                     color='red', marker='v', label='Продажи', s=50, alpha=0.7)
                
                axes[0, 1].plot(df.index, df['current_price'], color='black', alpha=0.5, label='Цена BTC', linewidth=1)
                axes[0, 1].set_title('Активность ордеров', fontsize=12, fontweight='bold')
                axes[0, 1].legend()
                axes[0, 1].grid(True, alpha=0.3)
                axes[0, 1].set_ylabel('Цена (USDT)', fontsize=10)
            
            # 3. AI оптимизации
            if analysis['ai_decisions']:
                ai_df = pd.DataFrame(analysis['ai_decisions'])
                ai_df['timestamp'] = pd.to_datetime(ai_df['timestamp'], unit='s')
                
                axes[1, 0].plot(ai_df['timestamp'], ai_df['new_levels'], marker='o', 
                              color='purple', linewidth=2, markersize=6)
                axes[1, 0].set_title('AI Оптимизация уровней сетки', fontsize=12, fontweight='bold')
                axes[1, 0].set_ylabel('Уровни сетки', fontsize=10)
                axes[1, 0].grid(True, alpha=0.3)
                
                # Добавляем второй график для расстояния
                ax2 = axes[1, 0].twinx()
                ax2.plot(ai_df['timestamp'], ai_df['new_spacing'] * 100, marker='s',
                        color='orange', linewidth=2, markersize=4, linestyle='--')
                ax2.set_ylabel('Расстояние (%)', fontsize=10, color='orange')
                ax2.tick_params(axis='y', labelcolor='orange')
            
            # 4. Просадка
            cumulative_max = df['total_balance_usdt'].cummax()
            drawdown = ((cumulative_max - df['total_balance_usdt']) / cumulative_max) * 100
            axes[1, 1].fill_between(df.index, 0, drawdown, alpha=0.3, color='red')
            axes[1, 1].set_title('Просадка (%)', fontsize=12, fontweight='bold')
            axes[1, 1].set_ylabel('Просадка %', fontsize=10)
            axes[1, 1].grid(True, alpha=0.3)
            axes[1, 1].set_ylim(0, max(drawdown.max() * 1.1, 10))
            
            # 5. ROI по дням
            if len(df) > 100:
                daily_roi = df['roi_percentage'].resample('D').last()
                axes[2, 0].bar(daily_roi.index, daily_roi.values, alpha=0.7, color='skyblue')
                axes[2, 0].set_title('Дневная доходность (ROI%)', fontsize=12, fontweight='bold')
                axes[2, 0].set_ylabel('ROI %', fontsize=10)
                axes[2, 0].grid(True, alpha=0.3, axis='y')
                axes[2, 0].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
            
            # 6. Распределение сделок
            if analysis['order_history']:
                orders_by_hour = pd.DataFrame(analysis['order_history'])
                orders_by_hour['timestamp'] = pd.to_datetime(orders_by_hour['timestamp'])
                orders_by_hour['hour'] = orders_by_hour['timestamp'].dt.hour
                hour_counts = orders_by_hour['hour'].value_counts().sort_index()
                
                axes[2, 1].bar(hour_counts.index, hour_counts.values, alpha=0.7, color='teal')
                axes[2, 1].set_title('Распределение сделок по часам', fontsize=12, fontweight='bold')
                axes[2, 1].set_xlabel('Час дня', fontsize=10)
                axes[2, 1].set_ylabel('Количество сделок', fontsize=10)
                axes[2, 1].grid(True, alpha=0.3, axis='y')
                axes[2, 1].set_xticks(range(0, 24, 3))
            
            plt.tight_layout(rect=[0, 0.03, 1, 0.95])
            plt.savefig('advanced_backtest_charts.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            print("✅ Расширенные графики сохранены в: advanced_backtest_charts.png")
            
        except Exception as e:
            print(f"⚠️ Ошибка создания графиков: {e}")
            import traceback
            print(f"Детали: {traceback.format_exc()}")

    def _generate_advanced_html_report(self, analysis, days, timestamp_str):
        """🔧 ГЕНЕРАЦИЯ РАСШИРЕННОГО HTML ОТЧЕТА"""
        summary = analysis['summary']
        advanced = analysis['advanced_metrics']
        params = analysis['parameters']
        final_balances = analysis['final_balances']
        
        profit_class = 'positive' if summary['total_profit'] > 0 else 'negative'
        vs_hodl_class = 'positive' if summary['vs_hodl'] > 0 else 'negative'
        sharpe_color = 'green' if advanced['sharpe_ratio'] > 1 else 'orange' if advanced['sharpe_ratio'] > 0 else 'red'
        drawdown_color = 'green' if advanced['max_drawdown_percentage'] < 5 else 'orange' if advanced['max_drawdown_percentage'] < 10 else 'red'
        
        return f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Расширенный отчет тестирования Grid Bot v2.0</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #2c3e50, #4a6491); color: white; padding: 25px; border-radius: 10px; margin-bottom: 20px; }}
        .metric-card {{ background: white; padding: 20px; margin: 15px 0; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .positive {{ color: #27ae60; font-weight: bold; }}
        .negative {{ color: #e74c3c; font-weight: bold; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; }}
        .sharpe {{ color: {sharpe_color}; font-weight: bold; }}
        .drawdown {{ color: {drawdown_color}; font-weight: bold; }}
        .balance-section {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #3498db; }}
        .balance-item {{ display: flex; justify-content: space-between; margin: 8px 0; padding: 8px; background: white; border-radius: 4px; }}
        .metric-value {{ font-size: 1.2em; font-weight: bold; }}
        .metric-label {{ color: #7f8c8d; }}
        .section-title {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; margin-top: 30px; }}
        .chart-container {{ text-align: center; margin: 20px 0; }}
        .chart-img {{ max-width: 100%; border-radius: 8px; box-shadow: 0 3px 15px rgba(0,0,0,0.2); }}
        .summary-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .summary-table th, .summary-table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        .summary-table th {{ background: #f8f9fa; }}
        .summary-table tr:hover {{ background: #f5f5f5; }}
        .badge {{ display: inline-block; padding: 3px 8px; border-radius: 12px; font-size: 0.85em; margin-left: 10px; }}
        .badge-success {{ background: #d4edda; color: #155724; }}
        .badge-warning {{ background: #fff3cd; color: #856404; }}
        .badge-danger {{ background: #f8d7da; color: #721c24; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Расширенный отчет тестирования AI Grid Bot v2.0</h1>
        <p>Период: {days} дней | Режим: {'🤖 AI-оптимизация' if params.get('ai_mode', False) else '👨‍💻 Ручной'} | Дата теста: {timestamp_str}</p>
    </div>

    <div class="metrics-grid">
        <div class="metric-card">
            <h3>📈 Финансовые результаты</h3>
            <p>Общая прибыль: <span class="{profit_class} metric-value">{summary['total_profit']:+.2f} USDT ({summary['total_profit_percentage']:+.2f}%)</span></p>
            <p>Прибыль HODL: {summary['hodl_profit']:+.2f} USDT</p>
            <p>VS HODL: <span class="{vs_hodl_class} metric-value">{summary['vs_hodl']:+.2f} USDT</span></p>
            
            <div class="balance-section">
                <h4>💰 Финальные балансы:</h4>
                <div class="balance-item">
                    <span class="metric-label">USDT:</span>
                    <span class="metric-value">{final_balances['usdt']:.2f} USDT</span>
                </div>
                <div class="balance-item">
                    <span class="metric-label">BTC:</span>
                    <span class="metric-value">{final_balances['btc']:.6f} BTC</span>
                </div>
                <div class="balance-item">
                    <span class="metric-label">Последний курс BTC:</span>
                    <span class="metric-value">{final_balances['last_price']:.2f} USDT</span>
                </div>
                <div class="balance-item">
                    <span class="metric-label">Общая стоимость:</span>
                    <span class="metric-value">{final_balances['usdt'] + (final_balances['btc'] * final_balances['last_price']):.2f} USDT</span>
                </div>
            </div>
        </div>

        <div class="metric-card">
            <h3>📊 Статистика торговли</h3>
            <p>Всего сделок: <span class="metric-value">{summary['total_orders']}</span></p>
            <p>Сеток создано: <span class="metric-value">{summary['grid_count']}</span></p>
            <p>AI оптимизаций: <span class="metric-value">{summary['ai_optimizations']}</span></p>
            <p>Комиссии: <span class="metric-value">{summary['total_commission']:.4f} USDT</span></p>
            <p>Эффективность: <span class="metric-value">{summary['execution_efficiency']:.1f}%</span></p>
        </div>
    </div>

    <h2 class="section-title">📊 Расширенные метрики качества</h2>
    
    <table class="summary-table">
        <thead>
            <tr>
                <th>Метрика</th>
                <th>Значение</th>
                <th>Оценка</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Sharpe Ratio</td>
                <td><span class="sharpe metric-value">{advanced['sharpe_ratio']:.2f}</span></td>
                <td>{'<span class="badge badge-success">Отлично</span>' if advanced['sharpe_ratio'] > 1.5 else '<span class="badge badge-warning">Хорошо</span>' if advanced['sharpe_ratio'] > 0.5 else '<span class="badge badge-danger">Требует улучшения</span>'}</td>
            </tr>
            <tr>
                <td>Sortino Ratio</td>
                <td><span class="metric-value">{advanced['sortino_ratio']:.2f}</span></td>
                <td>{'<span class="badge badge-success">Низкий риск</span>' if advanced['sortino_ratio'] > 2 else '<span class="badge badge-warning">Умеренный риск</span>' if advanced['sortino_ratio'] > 1 else '<span class="badge badge-danger">Высокий риск</span>'}</td>
            </tr>
            <tr>
                <td>Максимальная просадка</td>
                <td><span class="drawdown metric-value">{advanced['max_drawdown_percentage']:.1f}%</span></td>
                <td>{'<span class="badge badge-success">Низкая</span>' if advanced['max_drawdown_percentage'] < 5 else '<span class="badge badge-warning">Умеренная</span>' if advanced['max_drawdown_percentage'] < 10 else '<span class="badge badge-danger">Высокая</span>'}</td>
            </tr>
            <tr>
                <td>Win Rate</td>
                <td><span class="metric-value">{advanced['win_rate']:.1f}%</span></td>
                <td>{'<span class="badge badge-success">Высокий</span>' if advanced['win_rate'] > 60 else '<span class="badge badge-warning">Средний</span>' if advanced['win_rate'] > 40 else '<span class="badge badge-danger">Низкий</span>'}</td>
            </tr>
            <tr>
                <td>Коэффициент восстановления</td>
                <td><span class="metric-value">{advanced['recovery_factor']:.2f}</span></td>
                <td>{'<span class="badge badge-success">Быстрое</span>' if advanced['recovery_factor'] > 3 else '<span class="badge badge-warning">Умеренное</span>' if advanced['recovery_factor'] > 1 else '<span class="badge badge-danger">Медленное</span>'}</td>
            </tr>
            <tr>
                <td>Прибыль на сделку</td>
                <td><span class="metric-value">{advanced['profit_per_trade']:.4f} USDT</span></td>
                <td>{'<span class="badge badge-success">Высокая</span>' if advanced['profit_per_trade'] > 0.1 else '<span class="badge badge-warning">Умеренная</span>' if advanced['profit_per_trade'] > 0 else '<span class="badge badge-danger">Убыточная</span>'}</td>
            </tr>
        </tbody>
    </table>

    <h2 class="section-title">📈 Визуализации расширенной симуляции</h2>
    <div class="chart-container">
        <img src="advanced_backtest_charts.png" alt="Графики расширенного тестирования" class="chart-img">
        <p><em>Рисунок 1: Комплексный анализ результатов симуляции</em></p>
    </div>

    <div class="metric-card">
        <h3>⚙️ Параметры тестирования</h3>
        <p>Начальный баланс: {params.get('initial_usdt', 0)} USDT + {params.get('initial_btc', 0)} BTC</p>
        <p>Режим: {'🤖 AI-оптимизация' if params.get('ai_mode', False) else '👨‍💻 Ручной'}</p>
        <p>Уровни сетки: {params.get('grid_levels', 0)}</p>
        <p>Расстояние: {params.get('grid_spacing', 0)*100:.2f}%</p>
        <p>Интервал пересоздания: {params.get('grid_refresh_time', 1800)} сек ({(params.get('grid_refresh_time', 1800)/60):.0f} мин)</p>
        <p>Период: {days} дней</p>
        <p>Записей в данных: {len(analysis['simulation_data']) if not analysis['simulation_data'].empty else 0}</p>
    </div>
</body>
</html>
"""

    def _save_text_report(self, analysis, days, timestamp_str):
        """📝 СОХРАНЕНИЕ КРАТКОГО ТЕКСТОВОГО ОТЧЕТА"""
        try:
            filename = f"quick_report_{days}days_{timestamp_str}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("КРАТКИЙ ОТЧЕТ СИМУЛЯЦИИ GRID BOT\n")
                f.write("=" * 60 + "\n\n")
                
                summary = analysis['summary']
                advanced = analysis['advanced_metrics']
                
                # Основные результаты
                f.write("ОСНОВНЫЕ РЕЗУЛЬТАТЫ:\n")
                f.write(f"  Прибыль: {summary['total_profit']:+.2f} USDT\n")
                f.write(f"  ROI: {summary['total_profit_percentage']:+.2f}%\n")
                f.write(f"  VS HODL: {summary['vs_hodl']:+.2f} USDT\n")
                f.write(f"  Сделок: {summary['total_orders']}\n")
                f.write(f"  Сеток: {summary['grid_count']}\n")
                f.write(f"  Комиссии: {summary['total_commission']:.4f} USDT\n\n")
                
                # Качество стратегии
                f.write("КАЧЕСТВО СТРАТЕГИИ:\n")
                f.write(f"  Sharpe Ratio: {advanced['sharpe_ratio']:.2f}\n")
                f.write(f"  Макс. просадка: {advanced['max_drawdown_percentage']:.1f}%\n")
                f.write(f"  Win Rate: {advanced['win_rate']:.1f}%\n")
                f.write(f"  Коэф. восстановления: {advanced['recovery_factor']:.2f}\n\n")
                
                # Рекомендации
                f.write("РЕКОМЕНДАЦИИ:\n")
                if advanced['sharpe_ratio'] < 0.5:
                    f.write("  ⚠️  Низкий Sharpe Ratio - стратегия недостаточно эффективна\n")
                if advanced['max_drawdown_percentage'] > 10:
                    f.write("  ⚠️  Высокая просадка - требуется улучшение управления рисками\n")
                if advanced['win_rate'] < 40:
                    f.write("  ⚠️  Низкий Win Rate - много убыточных сделок\n")
                if summary['execution_efficiency'] < 50:
                    f.write("  ⚠️  Низкая эффективность исполнения - ордера редко срабатывают\n")
                
                if (advanced['sharpe_ratio'] > 1 and 
                    advanced['max_drawdown_percentage'] < 5 and 
                    advanced['win_rate'] > 50):
                    f.write("  ✅ Стратегия показывает отличные результаты!\n")
            
            print(f"✅ Краткий отчет сохранен в: {filename}")
            
        except Exception as e:
            print(f"⚠️ Ошибка сохранения текстового отчета: {e}")

def run_advanced_historical_test():
    """🚀 ФУНКЦИЯ ЗАПУСКА ТОЧНОГО ТЕСТИРОВАНИЯ"""
    tester = AdvancedHistoricalTester()
    
    # Тест с реальными параметрами
    results = tester.run_complete_test(
        days=7,  # 7 дней для быстрого теста
        initial_balance=1000,
        initial_btc=0.01,
        ai_mode=True,
        force_reload=False
    )
    
    return results

# Для обратной совместимости
def run_historical_test_mode():
    """🔗 ФУНКЦИЯ ДЛЯ ОБРАТНОЙ СОВМЕСТИМОСТИ"""
    return run_advanced_historical_test()

if __name__ == "__main__":
    run_advanced_historical_test()
