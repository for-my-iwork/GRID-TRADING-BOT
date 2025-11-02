# analytics/reporter.py
"""
📊 ГЕНЕРАТОР ОТЧЕТОВ ДЛЯ ТОРГОВЛИ
"""

class ReportGenerator:
    """📊 ГЕНЕРАТОР ОТЧЕТОВ ДЛЯ ТОРГОВЛИ"""
    
    def __init__(self, telegram_bot=None):
        self.telegram_bot = telegram_bot

    def send_final_report(self, stats):
        """🏁 ОТПРАВКА ФИНАЛЬНОГО ОТЧЕТА"""
        if not self.telegram_bot:
            print("❌ Telegram бот не инициализирован для отправки отчета")
            return
            
        message = f"""
🏁 <b>ФИНАЛЬНЫЙ ОТЧЕТ v9.0</b>

💰 Начальный баланс: {stats.get('initial_balance', 0):.2f} USDT
💰 Конечный баланс: {stats.get('final_balance', 0):.2f} USDT
📊 Чистая прибыль: {stats.get('total_profit', 0):+.4f} USDT

📦 Статистика:
• Сеток создано: {stats.get('grid_count', 0)}
• Ордеров размещено: {stats.get('orders_created', 0)}
• Ордеров исполнено: {stats.get('orders_executed', 0)}
• Комиссий уплачено: {stats.get('total_commission', 0):.4f} USDT
• Ошибок API: {stats.get('api_errors', 0)}
• Время работы: {stats.get('running_time', '00:00')}
• Режим рынка: {stats.get('market_regime', 'Не определен')}
        """
        self.telegram_bot.send_message(message)

    def generate_performance_report(self, stats):
        """📈 ГЕНЕРАЦИЯ ОТЧЕТА О ПРОИЗВОДИТЕЛЬНОСТИ"""
        total_orders = stats.get('orders_created', 0)
        executed_orders = stats.get('orders_executed', 0)
        execution_rate = (executed_orders / total_orders * 100) if total_orders > 0 else 0
        
        report = f"""
📈 <b>ОТЧЕТ О ПРОИЗВОДИТЕЛЬНОСТИ</b>

📊 Эффективность сетки:
• Всего ордеров: {total_orders}
• Исполнено ордеров: {executed_orders}
• Процент исполнения: {execution_rate:.1f}%

💰 Финансовые показатели:
• Общая прибыль: {stats.get('total_profit', 0):+.4f} USDT
• Комиссии: {stats.get('total_commission', 0):.4f} USDT
• Чистая прибыль: {stats.get('total_profit', 0) - stats.get('total_commission', 0):+.4f} USDT

⏱️ Временные показатели:
• Время работы: {stats.get('running_time', '00:00')}
• Сеток создано: {stats.get('grid_count', 0)}
• Среднее время на сетку: {self.calculate_avg_grid_time(stats)}
        """
        return report

    def calculate_avg_grid_time(self, stats):
        """⏱️ РАСЧЕТ СРЕДНЕГО ВРЕМЕНИ НА СЕТКУ"""
        grid_count = stats.get('grid_count', 0)
        if grid_count == 0:
            return "N/A"
        
        running_time = stats.get('running_time', '00:00')
        try:
            hours, minutes = map(int, running_time.split(':'))
            total_minutes = hours * 60 + minutes
            avg_minutes = total_minutes / grid_count
            return f"{avg_minutes:.1f} мин"
        except:
            return "N/A"
