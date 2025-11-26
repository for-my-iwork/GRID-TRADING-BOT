# historical_tester.py
"""
📊 ТЕСТИРОВАНИЕ НА ИСТОРИЧЕСКИХ ДАННЫХ ДЛЯ GRID BOT
"""

import time
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional
from utils.api_client import APIClient


class HistoricalTester:
    """📊 ТЕСТЕР НА ИСТОРИЧЕСКИХ ДАННЫХ"""
    
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.historical_data = []
        self.test_results = {}
        self.symbol = "BTCUSDT"
        
    def fetch_historical_data(self, days: int = 365, 
                            interval: str = "60") -> bool:
        """
        📥 ЗАГРУЗКА ИСТОРИЧЕСКИХ ДАННЫХ С ПРОГРЕСС-БАРОМ
        
        Args:
            days: Количество дней для загрузки
            interval: Интервал в минутах
            
        Returns:
            bool: Успешность загрузки
        """
        print(f"📥 Загрузка исторических данных за {days} дней...")
        
        end_time = int(datetime.now().timestamp() * 1000)
        start_time = int((datetime.now() - 
                         timedelta(days=days)).timestamp() * 1000)
        
        all_data = []
        current_start = start_time
        
        total_requests = (end_time - start_time) // (1000 * 60 * 60 * 24 * 30) + 1
        
        with tqdm(total=total_requests, desc="📊 Загрузка данных") as pbar:
            while current_start < end_time:
                try:
                    response = self.api_client.session.get_kline(
                        category="spot",
                        symbol=self.symbol,
                        interval=interval,
                        start=current_start,
                        limit=200
                    )
                    
                    if response and response['retCode'] == 0:
                        kline_data = response['result']['list']
                        if not kline_data:
                            break
                            
                        all_data.extend(kline_data)
                        last_timestamp = int(kline_data[-1][0])
                        current_start = last_timestamp + 1
                        
                        pbar.update(1)
                        pbar.set_postfix({
                            'Свечей': len(all_data),
                            'Дата': datetime.fromtimestamp(
                                last_timestamp/1000).strftime('%Y-%m-%d')
                        })
                        
                        time.sleep(0.1)
                    else:
                        error_msg = response.get('retMsg', 'Unknown error')
                        print(f"❌ Ошибка API: {error_msg}")
                        break
                        
                except Exception as e:
                    print(f"❌ Ошибка при загрузке данных: {e}")
                    break
        
        if all_data:
            self.historical_data = sorted(all_data, key=lambda x: int(x[0]))
            print(f"✅ Успешно загружено {len(self.historical_data)} свечей")
            return True
        else:
            print("❌ Не удалось загрузить исторические данные")
            return False

    def prepare_test_data(self) -> pd.DataFrame:
        """📊 ПОДГОТОВКА ДАННЫХ ДЛЯ ТЕСТИРОВАНИЯ"""
        if not self.historical_data:
            print("❌ Нет данных для тестирования")
            return pd.DataFrame()
            
        print("📊 Подготовка данных для тестирования...")
        
        df_data = []
        for candle in tqdm(self.historical_data, desc="🔄 Обработка свечей"):
            df_data.append({
                'timestamp': datetime.fromtimestamp(int(candle[0]) / 1000),
                'open': float(candle[1]),
                'high': float(candle[2]),
                'low': float(candle[3]),
                'close': float(candle[4]),
                'volume': float(candle[5])
            })
        
        df = pd.DataFrame(df_data)
        df.set_index('timestamp', inplace=True)
        
        print(f"✅ Данные подготовлены: {len(df)} записей")
        print(f"📅 Период: {df.index[0]} - {df.index[-1]}")
        
        return df

    def run_historical_backtest(self, bot_params: Dict, 
                              test_data: pd.DataFrame) -> Dict:
        """
        🧪 ЗАПУСК ТЕСТИРОВАНИЯ НА ИСТОРИЧЕСКИХ ДАННЫХ
        
        Args:
            bot_params: Параметры бота для тестирования
            test_data: DataFrame с историческими данными
            
        Returns:
            Dict: Результаты тестирования
        """
        print("🧪 Запуск исторического тестирования...")
        
        simulator = HistoricalSimulator(bot_params)
        results = []
        
        with tqdm(total=len(test_data), desc="🧪 Тестирование") as pbar:
            for idx, (timestamp, row) in enumerate(test_data.iterrows()):
                current_price = row['close']
                
                result = simulator.update(current_price, timestamp)
                results.append(result)
                
                if idx % 100 == 0:
                    pbar.update(100)
                    pbar.set_postfix({
                        'Прибыль': f"{result['total_profit']:+.2f}",
                        'Цена': f"{current_price:.1f}",
                        'Ордеров': result['orders_executed']
                    })
        
        analysis = self.analyze_backtest_results(results, bot_params)
        
        print("✅ Тестирование завершено")
        return analysis

    def analyze_backtest_results(self, results: List[Dict], 
                               bot_params: Dict) -> Dict:
        """📈 АНАЛИЗ РЕЗУЛЬТАТОВ ТЕСТИРОВАНИЯ"""
        print("📈 Анализ результатов...")
        
        df = pd.DataFrame(results)
        
        total_profit = df['total_profit'].iloc[-1]
        max_profit = df['total_profit'].max()
        min_profit = df['total_profit'].min()
        max_drawdown = (df['total_profit'].cummax() - 
                       df['total_profit']).max()
        
        profit_volatility = df['total_profit'].pct_change().std()
        
        total_orders = df['orders_executed'].iloc[-1]
        profitable_trades = len(df[df['trade_profit'] > 0])
        loss_trades = len(df[df['trade_profit'] < 0])
        win_rate = (profitable_trades / total_orders 
                   if total_orders > 0 else 0)
        
        initial_balance = bot_params.get('initial_balance', 1000)
        profit_percentage = (total_profit / initial_balance) * 100
        drawdown_percentage = (max_drawdown / max_profit * 100 
                              if max_profit > 0 else 0)
        sharpe_ratio = ((total_profit / 365) / profit_volatility 
                       if profit_volatility > 0 else 0)
        
        analysis = {
            'total_profit': total_profit,
            'total_profit_percentage': profit_percentage,
            'max_profit': max_profit,
            'min_profit': min_profit,
            'max_drawdown': max_drawdown,
            'max_drawdown_percentage': drawdown_percentage,
            'profit_volatility': profit_volatility,
            'total_orders': total_orders,
            'profitable_trades': profitable_trades,
            'loss_trades': loss_trades,
            'win_rate': win_rate,
            'sharpe_ratio': sharpe_ratio,
            'parameters': bot_params,
            'results_dataframe': df
        }
        
        return analysis

    def generate_test_report(self, analysis: Dict, 
                           save_path: str = "backtest_report.html"):
        """📄 ГЕНЕРАЦИЯ ДЕТАЛЬНОГО ОТЧЕТА"""
        print("📄 Генерация отчета...")
        
        df = analysis['results_dataframe']
        
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        axes[0, 0].plot(df.index, df['total_profit'], 
                       label='Общая прибыль', color='green')
        axes[0, 0].set_title('Динамика прибыли')
        axes[0, 0].set_ylabel('Прибыль (USDT)')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        cumulative_max = df['total_profit'].cummax()
        drawdown = cumulative_max - df['total_profit']
        axes[0, 1].fill_between(df.index, 0, drawdown, 
                               alpha=0.3, color='red', label='Просадка')
        axes[0, 1].set_title('Максимальная просадка')
        axes[0, 1].set_ylabel('Просадка (USDT)')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        
        trade_profits = df[df['trade_profit'] != 0]['trade_profit']
        if len(trade_profits) > 0:
            axes[1, 0].hist(trade_profits, bins=50, alpha=0.7, color='blue')
            axes[1, 0].axvline(0, color='red', linestyle='--', 
                              label='Безубыток')
            axes[1, 0].set_title('Распределение прибыли по сделкам')
            axes[1, 0].set_xlabel('Прибыль/Убыток (USDT)')
            axes[1, 0].legend()
        
        df['hour'] = df.index.hour
        trades_by_hour = df[df['trade_profit'] != 0].groupby('hour').size()
        axes[1, 1].bar(trades_by_hour.index, trades_by_hour.values, 
                      alpha=0.7, color='orange')
        axes[1, 1].set_title('Количество сделок по часам')
        axes[1, 1].set_xlabel('Час дня')
        axes[1, 1].set_ylabel('Количество сделок')
        
        plt.tight_layout()
        plt.savefig('backtest_charts.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        html_report = self._generate_html_report(analysis)
        
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        print(f"✅ Отчет сохранен: {save_path}")
        return save_path

    def _generate_html_report(self, analysis: Dict) -> str:
        """🔧 ГЕНЕРАЦИЯ HTML ОТЧЕТА"""
        params = analysis['parameters']
        profit = analysis['total_profit']
        profit_class = 'positive' if profit > 0 else 'negative'
        profit_pct = analysis['total_profit_percentage']
        
        html = f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <title>Отчет по тестированию Grid Bot</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #2c3e50; color: white; padding: 20px; }}
                .metric {{ background: #ecf0f1; padding: 15px; margin: 10px 0; }}
                .positive {{ color: #27ae60; font-weight: bold; }}
                .negative {{ color: #e74c3c; font-weight: bold; }}
                .parameters {{ background: #34495e; color: white; padding: 15px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Отчет по тестированию Grid Trading Bot</h1>
                <p>Сгенерировано: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <h2>📈 Основные метрики</h2>
            <table>
                <tr><td>Общая прибыль</td>
                    <td class="{profit_class}">{profit:+.2f} USDT ({profit_pct:+.2f}%)</td></tr>
                <tr><td>Максимальная прибыль</td>
                    <td>{analysis['max_profit']:.2f} USDT</td></tr>
                <tr><td>Максимальная просадка</td>
                    <td class="negative">{analysis['max_drawdown']:.2f} USDT</td></tr>
                <tr><td>Всего сделок</td><td>{analysis['total_orders']}</td></tr>
                <tr><td>Прибыльные сделки</td>
                    <td>{analysis['profitable_trades']} ({analysis['win_rate']:.1%})</td></tr>
                <tr><td>Убыточные сделки</td><td>{analysis['loss_trades']}</td></tr>
                <tr><td>Коэффициент Шарпа</td><td>{analysis['sharpe_ratio']:.2f}</td></tr>
            </table>
            
            <h2>⚙️ Параметры тестирования</h2>
            <div class="parameters">
                <table>
                    <tr><td>Уровни сетки</td><td>{params.get('grid_levels', 'N/A')}</td></tr>
                    <tr><td>Размер ордера</td><td>{params.get('order_size', 'N/A')} BTC</td></tr>
                    <tr><td>Расстояние сетки</td>
                        <td>{params.get('grid_spacing', 'N/A')*100:.2f}%</td></tr>
                    <tr><td>Начальный баланс</td>
                        <td>{params.get('initial_balance', 'N/A')} USDT</td></tr>
                    <tr><td>Режим AI</td>
                        <td>{'Да' if params.get('ai_mode', False) else 'Нет'}</td></tr>
                </table>
            </div>
            
            <h2>📊 Визуализации</h2>
            <img src="backtest_charts.png" alt="Графики тестирования" style="max-width: 100%;">
            
            <h2>📋 Рекомендации</h2>
            {self._generate_recommendations(analysis)}
        </body>
        </html>
        """
        
        return html

    def _generate_recommendations(self, analysis: Dict) -> str:
        """💡 ГЕНЕРАЦИЯ РЕКОМЕНДАЦИЙ НА ОСНОВЕ РЕЗУЛЬТАТОВ"""
        recommendations = []
        
        if analysis['win_rate'] < 0.5:
            recommendations.append("❌ Низкий процент прибыльных сделок. "
                                 "Рассмотрите увеличение расстояния между уровнями.")
        
        if analysis['max_drawdown_percentage'] > 20:
            recommendations.append("⚠️ Высокая максимальная просадка. "
                                 "Увеличьте стоп-лосс или уменьшите размер позиции.")
        
        if analysis['total_profit'] < 0:
            recommendations.append("🔻 Стратегия убыточна на исторических данных. "
                                 "Пересмотрите параметры сетки.")
        
        if analysis['sharpe_ratio'] < 1:
            recommendations.append("📉 Низкий коэффициент Шарпа. "
                                 "Стратегия имеет низкую эффективность относительно риска.")
        
        if analysis['profit_volatility'] > 0.1:
            recommendations.append("🎢 Высокая волатильность прибыли. "
                                 "Рассмотрите более консервативные параметры.")
        
        if not recommendations:
            recommendations.append("✅ Стратегия показывает хорошие результаты! "
                                 "Можете использовать эти параметры для реальной торговли.")
        
        return "<ul>" + "".join([f"<li>{rec}</li>" for rec in recommendations]) + "</ul>"


class HistoricalSimulator:
    """🎮 СИМУЛЯТОР ТОРГОВЛИ ДЛЯ ИСТОРИЧЕСКИХ ДАННЫХ"""
    
    def __init__(self, bot_params: Dict):
        self.params = bot_params
        self.current_balance = bot_params.get('initial_balance', 1000)
        self.btc_balance = 0
        self.active_orders = []
        self.total_profit = 0
        self.orders_executed = 0
        self.trade_profit = 0
        self.grid_levels = bot_params.get('grid_levels', 5)
        self.order_size = bot_params.get('order_size', 0.001)
        self.grid_spacing = bot_params.get('grid_spacing', 0.003)
        
    def update(self, current_price: float, timestamp: datetime) -> Dict:
        """
        🔄 ОБНОВЛЕНИЕ СИМУЛЯЦИИ ДЛЯ ТЕКУЩЕЙ ЦЕНЫ
        
        Returns:
            Dict: Текущее состояние симуляции
        """
        self._check_orders(current_price)
        
        if len(self.active_orders) < self.grid_levels * 2:
            self._create_grid_orders(current_price)
        
        return {
            'timestamp': timestamp,
            'price': current_price,
            'total_profit': self.total_profit,
            'current_balance': self.current_balance,
            'btc_balance': self.btc_balance,
            'active_orders': len(self.active_orders),
            'orders_executed': self.orders_executed,
            'trade_profit': self.trade_profit
        }
    
    def _create_grid_orders(self, current_price: float):
        """📊 СОЗДАНИЕ ОРДЕРОВ СЕТКИ"""
        buy_prices = [current_price * (1 - i * self.grid_spacing) 
                     for i in range(1, self.grid_levels + 1)]
        sell_prices = [current_price * (1 + i * self.grid_spacing) 
                      for i in range(1, self.grid_levels + 1)]
        
        for price in buy_prices:
            if self.current_balance > self.order_size * price:
                self.active_orders.append({
                    'type': 'buy',
                    'price': price,
                    'quantity': self.order_size
                })
        
        for price in sell_prices:
            if self.btc_balance > self.order_size:
                self.active_orders.append({
                    'type': 'sell', 
                    'price': price,
                    'quantity': self.order_size
                })
    
    def _check_orders(self, current_price: float):
        """✅ ПРОВЕРКА ИСПОЛНЕНИЯ ОРДЕРОВ"""
        executed_orders = []
        
        for order in self.active_orders:
            buy_condition = (order['type'] == 'buy' and 
                           current_price <= order['price'])
            sell_condition = (order['type'] == 'sell' and 
                            current_price >= order['price'])
            
            if buy_condition or sell_condition:
                executed_orders.append(order)
                
                if order['type'] == 'buy':
                    cost = order['quantity'] * order['price']
                    if self.current_balance >= cost:
                        self.current_balance -= cost
                        self.btc_balance += order['quantity']
                        self.trade_profit = -cost
                else:
                    revenue = order['quantity'] * order['price'] 
                    if self.btc_balance >= order['quantity']:
                        self.btc_balance -= order['quantity']
                        self.current_balance += revenue
                        self.trade_profit = revenue
                
                self.orders_executed += 1
                self.total_profit += self.trade_profit
        
        for order in executed_orders:
            self.active_orders.remove(order)


def run_historical_test_mode():
    """🚀 ЗАПУСК РЕЖИМА ИСТОРИЧЕСКОГО ТЕСТИРОВАНИЯ"""
    print("🧪 ЗАПУСК РЕЖИМА ИСТОРИЧЕСКОГО ТЕСТИРОВАНИЯ")
    print("=" * 50)
    
    api_client = APIClient()
    tester = HistoricalTester(api_client)
    
    if not tester.fetch_historical_data(days=180):
        return
    
    test_data = tester.prepare_test_data()
    if test_data.empty:
        return
    
    bot_params = {
        'grid_levels': 5,
        'order_size': 0.001,
        'grid_spacing': 0.003,
        'initial_balance': 1000,
        'ai_mode': False
    }
    
    results = tester.run_historical_backtest(bot_params, test_data)
    report_path = tester.generate_test_report(results)
    
    print(f"✅ Тестирование завершено! Отчет: {report_path}")
    print("📊 Основные результаты:")
    print(f"   Общая прибыль: {results['total_profit']:+.2f} USDT")
    print(f"   Макс. просадка: {results['max_drawdown']:.2f} USDT")
    print(f"   Всего сделок: {results['total_orders']}")
    print(f"   Процент прибыльных: {results['win_rate']:.1%}")


if __name__ == "__main__":
    run_historical_test_mode()
