# telegram/commands.py
"""
📱 ОБРАБОТКА КОМАНД TELEGRAM ДЛЯ GRID BOT
"""

import time
from datetime import datetime

class TelegramCommands:
    """📱 ОБРАБОТКА КОМАНД TELEGRAM ДЛЯ GRID BOT"""
    
    def __init__(self, telegram_bot, api_client):
        self.telegram_bot = telegram_bot
        self.api_client = api_client
        self.command_cooldown = {}

    def process_command(self, command, bot_instance):
        """⚙️ ОСНОВНОЙ ОБРАБОТЧИК КОМАНД"""
        command = command.lower().strip()
        
        current_time = time.time()
        if command in self.command_cooldown:
            if current_time - self.command_cooldown[command] < 5:
                self.telegram_bot.send_message("⏳ Слишком частые команды. Подождите 5 секунд.")
                return
        
        self.command_cooldown[command] = current_time
        
        if command == '/stop':
            self.handle_stop_command(bot_instance)
        elif command == '/emergency_stop':
            self.handle_emergency_stop_command(bot_instance)
        elif command == '/status':
            self.handle_status_command(bot_instance)
        elif command == '/balance':
            self.handle_balance_command(bot_instance)
        elif command == '/params':
            self.handle_params_command(bot_instance)
        elif command == '/help':
            self.handle_help_command()
        elif command == '/start':
            self.handle_start_command(bot_instance)
        elif command == '/restart':
            self.handle_restart_command(bot_instance)
        else:
            self.handle_unknown_command(command)

    def handle_stop_command(self, bot_instance):
        """🛑 ОБРАБОТКА КОМАНДЫ МЯГКОЙ ОСТАНОВКИ"""
        bot_instance.user_commanded_stop = True
        self.telegram_bot.send_message("🛑 Получена команда мягкой остановки...")

    def handle_emergency_stop_command(self, bot_instance):
        """🚨 ОБРАБОТКА КОМАНДЫ АВАРИЙНОЙ ОСТАНОВКИ"""
        bot_instance.user_commanded_emergency_stop = True
        self.telegram_bot.send_message("🚨 АВАРИЙНАЯ ОСТАНОВКА! Отменяю все ордера...")

    def handle_status_command(self, bot_instance):
        """📊 ОБРАБОТКА КОМАНДЫ СТАТУСА"""
        try:
            current_price = self.api_client.get_current_price('BTCUSDT')
            usdt, btc = self.api_client.get_balance()
            total = usdt + (btc * current_price) if current_price else 0
            
            status = f"""
📊 <b>ТЕКУЩИЙ СТАТУС v9.0</b>

⏰ Время работы: {bot_instance.get_running_time()}
💰 Баланс: {usdt:.2f} USDT + {btc:.6f} BTC
💵 Общий: {total:.2f} USDT
🎯 Цена: {current_price:.1f}

📦 Статистика:
• Сеток: #{bot_instance.grid_count}
• Ордеров создано: {bot_instance.total_orders_created}
• Ордеров исполнено: {bot_instance.executed_orders_count}
• Ошибок API: {bot_instance.api_errors}
• Комиссий: {bot_instance.total_commission:.4f} USDT
            """
            self.telegram_bot.send_message(status)
        except Exception as e:
            error_msg = f"❌ Ошибка получения статуса: {e}"
            self.telegram_bot.send_message(error_msg)

    def handle_balance_command(self, bot_instance):
        """💰 ОБРАБОТКА КОМАНДЫ БАЛАНСА"""
        try:
            current_price = self.api_client.get_current_price('BTCUSDT')
            usdt, btc = self.api_client.get_balance()
            total = usdt + (btc * current_price) if current_price else 0
            
            if hasattr(bot_instance, 'initial_usdt') and hasattr(bot_instance, 'initial_btc'):
                initial_total = bot_instance.initial_usdt + (bot_instance.initial_btc * getattr(bot_instance, 'initial_price', current_price))
                profit = total - initial_total
                profit_pct = (profit / initial_total * 100) if initial_total > 0 else 0
            else:
                profit = 0
                profit_pct = 0
            
            report = f"""
💰 <b>БАЛАНС И PnL</b>

💵 Текущий баланс: {total:.2f} USDT
📊 В том числе:
   - USDT: {usdt:.2f}
   - BTC: {btc:.6f} ({btc * current_price:.2f} USDT)

📈 Прибыль/убыток: {profit:+.2f} USDT ({profit_pct:+.2f}%)
💸 Комиссии: {bot_instance.total_commission:.4f} USDT
            """
            self.telegram_bot.send_message(report)
        except Exception as e:
            error_msg = f"❌ Ошибка получения баланса: {e}"
            self.telegram_bot.send_message(error_msg)

    def handle_params_command(self, bot_instance):
        """⚙️ ОБРАБОТКА КОМАНДЫ ПАРАМЕТРОВ"""
        try:
            params = f"""
⚙️ <b>ТЕКУЩИЕ ПАРАМЕТРЫ v9.0</b>

🎯 Символ: {bot_instance.symbol}
📊 Уровней: {bot_instance.grid_levels}
📦 Размер ордера: {bot_instance.order_size} BTC
📏 Расстояние: {bot_instance.grid_spacing*100:.2f}%
🔄 Обновление сетки: {bot_instance.grid_refresh_time} сек
⏱️ Время работы: {bot_instance.monitoring_duration} мин

🛡️ Защита:
• Стоп-лосс: {bot_instance.risk_manager.stop_loss_pct*100}%
• Макс. просадка: {bot_instance.risk_manager.max_drawdown_pct*100}%

🤖 Режим: {'AI-оптимизация' if bot_instance.ai_mode else 'Ручной'}
📊 Режим рынка: {getattr(bot_instance, 'market_regime', 'Не определен')}
            """
            self.telegram_bot.send_message(params)
        except Exception as e:
            error_msg = f"❌ Ошибка получения параметров: {e}"
            self.telegram_bot.send_message(error_msg)

    def handle_help_command(self):
        """ℹ️ ОБРАБОТКА КОМАНДЫ ПОМОЩИ"""
        help_text = """
🤖 <b>GRID BOT v9.0 - ДОСТУПНЫЕ КОМАНДЫ:</b>

/stop - Мягкая остановка
/emergency_stop - Аварийная остановка
/status - Текущий статус
/balance - Баланс и PnL
/params - Параметры сетки
/help - Справка
        """
        self.telegram_bot.send_message(help_text)

    def handle_start_command(self, bot_instance):
        """🚀 ОБРАБОТКА КОМАНДЫ START"""
        start_text = """
🚀 <b>GRID TRADING BOT v9.0</b>

🤖 Успешно запущен и работает!
        """
        self.telegram_bot.send_message(start_text)

    def handle_restart_command(self, bot_instance):
        """🔄 ОБРАБОТКА КОМАНДЫ ПЕРЕЗАПУСКА"""
        self.telegram_bot.send_message("🔄 Функция перезапуска в разработке")

    def handle_unknown_command(self, command):
        """❓ ОБРАБОТКА НЕИЗВЕСТНОЙ КОМАНДЫ"""
        self.telegram_bot.send_message(f"❓ Неизвестная команда: {command}")

    def cleanup(self):
        """🧹 ОЧИСТКА РЕСУРСОВ"""
        self.command_cooldown.clear()
