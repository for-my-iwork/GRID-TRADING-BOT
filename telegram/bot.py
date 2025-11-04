# telegram/bot.py
"""
📱 TELEGRAM БОТ ДЛЯ УПРАВЛЕНИЯ И УВЕДОМЛЕНИЙ v9.0
"""

import requests
import time
from datetime import datetime
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_POLLING_INTERVAL
from .commands import TelegramCommands

class TelegramBot:
    """📱 TELEGRAM БОТ ДЛЯ УПРАВЛЕНИЯ И УВЕДОМЛЕНИЙ"""
    
    def __init__(self, api_client):
        self.token = TELEGRAM_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.last_update_id = 0
        self.commands_handler = TelegramCommands(self, api_client)

    def send_message(self, message):
        """📨 ОТПРАВКА СООБЩЕНИЯ В TELEGRAM"""
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, data=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Ошибка отправки в Telegram: {e}")
            return False

    def send_start_alert(self, data):
        """🚀 УВЕДОМЛЕНИЕ О ЗАПУСКЕ БОТА"""
        message = f"""
🚀 <b>GRID BOT v9.0 ЗАПУЩЕН</b>

⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🎯 Символ: BTCUSDT
💰 Баланс: {data.get('usdt_balance', 0):.2f} USDT + {data.get('btc_balance', 0):.6f} BTC
📊 Режим: {'🤖 AI-оптимизация' if data.get('ai_mode', False) else '👨‍💻 Ручной'}
⏱️ Время работы: {data.get('duration', 0)} минут ({data.get('duration', 0)/60:.1f} часов)
        """
        return self.send_message(message)

    def send_order_alert(self, data):
        """✅ УВЕДОМЛЕНИЕ ОБ ИСПОЛНЕНИИ ОРДЕРА С КОМИССИЕЙ"""
        side = data.get('side', 'UNKNOWN')
        qty = data.get('qty', 0)
        price = data.get('price', 0)
        commission = data.get('commission', 0)
        timestamp = data.get('timestamp', 'N/A')
        
        trade_value = qty * price
        commission_percentage = (commission / trade_value * 100) if trade_value > 0 else 0
        
        message = f"""
✅ <b>ОРДЕР ИСПОЛНЕН</b>

{'🟢 ПОКУПКА' if side == 'BUY' else '🔴 ПРОДАЖА'} {qty:.6f} BTC
💵 Цена: {price:,.1f} USDT
💸 Сумма: {trade_value:,.2f} USDT
💳 Комиссия: {commission:.4f} USDT ({commission_percentage:.4f}%)
⏰ Время: {timestamp}
        """
        return self.send_message(message)

    def send_grid_alert(self, data):
        """🔄 УВЕДОМЛЕНИЕ О СОЗДАНИИ СЕТКИ"""
        message = f"""
🔄 <b>СЕТКА ОБНОВЛЕНА</b>

📊 Сетка: #{data.get('grid_count', 0)}
🎯 Текущая цена: {data.get('current_price', 0):,.1f}
📈 Уровней: {data.get('levels', 0)} в каждую сторону
📏 Расстояние: {data.get('spacing', 0)*100:.2f}%
📦 Ордеров размещено: {data.get('orders_placed', 0)}
        """
        return self.send_message(message)

    def send_ai_optimization_alert(self, data):
        """🧠 УВЕДОМЛЕНИЕ О AI ОПТИМИЗАЦИИ"""
        message = f"""
🧠 <b>AI ОПТИМИЗАЦИЯ</b>

📈 Волатильность: {data.get('volatility', 0)*100:.2f}%
📏 Расстояние: {data.get('old_spacing', 0)*100:.2f}% → {data.get('new_spacing', 0)*100:.2f}%
📊 Уровни: {data.get('old_levels', 0)} → {data.get('new_levels', 0)}
📊 Режим рынка: {data.get('market_regime', 'N/A')}
        """
        return self.send_message(message)

    def send_periodic_report(self, data):
        """📊 ПЕРИОДИЧЕСКИЙ ОТЧЕТ С КОМИССИЯМИ"""
        try:
            # Получаем данные о комиссиях (если переданы)
            maker_fee = data.get('maker_fee', 0.1)  # Значение по умолчанию 0.1%
            taker_fee = data.get('taker_fee', 0.1)  # Значение по умолчанию 0.1%
            
            message = f"""
📊 <b>ПЕРИОДИЧЕСКИЙ ОТЧЕТ v9.0</b>

⏰ Время работы: {data.get('running_time', '00:00')}
💰 Текущий баланс: {data.get('usdt_balance', 0):.2f} USDT + {data.get('btc_balance', 0):.6f} BTC
💵 Общий в USDT: {data.get('total_balance', 0):.2f}
📈 Прибыль: {data.get('profit', 0):+.4f} USDT
💸 Комиссии: {data.get('commission', 0):.4f} USDT
🎯 Ставки: M:{maker_fee:.4f}% / T:{taker_fee:.4f}%
📦 Исполнено ордеров: {data.get('executed_orders', 0)}
🔄 Сеток создано: {data.get('grid_count', 0)}
❌ Ошибок API: {data.get('api_errors', 0)}
            """
            return self.send_message(message)
        except Exception as e:
            print(f"❌ Ошибка формирования периодического отчета: {e}")
            # Отправка упрощенного отчета в случае ошибки
            simplified_message = f"""
📊 <b>ПЕРИОДИЧЕСКИЙ ОТЧЕТ</b>

⏰ Время работы: {data.get('running_time', '00:00')}
💰 Баланс: {data.get('total_balance', 0):.2f} USDT
📈 Прибыль: {data.get('profit', 0):+.4f} USDT
💸 Комиссии: {data.get('commission', 0):.4f} USDT
            """
            return self.send_message(simplified_message)

    def send_stop_alert(self, data):
        """🚨 УВЕДОМЛЕНИЕ ОБ ОСТАНОВКЕ"""
        message = f"""
🚨 <b>СРАБОТАЛ СТОП-МЕХАНИЗМ</b>

Причина: {data.get('reason', 'Неизвестно')}
Прибыль: {data.get('profit', 0):+.4f} USDT
Время работы: {data.get('running_time', '00:00')}
        """
        return self.send_message(message)

    def send_error_alert(self, data):
        """❌ УВЕДОМЛЕНИЕ ОБ ОШИБКЕ"""
        message = f"""
❌ <b>ОШИБКА БОТА v9.0</b>

Ошибка: {data.get('error', 'Неизвестная ошибка')}
Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        return self.send_message(message)

    def send_commission_update_alert(self, data):
        """💰 УВЕДОМЛЕНИЕ ОБ ОБНОВЛЕНИИ КОМИССИЙ"""
        message = f"""
💰 <b>ОБНОВЛЕНИЕ КОМИССИЙ</b>

🎯 Ставки комиссий обновлены:
   • Maker: {data.get('maker_fee', 0)*100:.4f}%
   • Taker: {data.get('taker_fee', 0)*100:.4f}%
⏰ Время: {datetime.now().strftime('%H:%M:%S')}
        """
        return self.send_message(message)

    def check_commands(self, bot_instance):
        """📲 ПРОВЕРКА КОМАНД ОТ ПОЛЬЗОВАТЕЛЯ С ЗАЩИТОЙ ОТ СТАРЫХ СООБЩЕНИЙ"""
        try:
            url = f"https://api.telegram.org/bot{self.token}/getUpdates"
            params = {
                'offset': self.last_update_id + 1,
                'timeout': 5
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('ok') and data.get('result'):
                    for update in data['result']:
                        self.last_update_id = update['update_id']
                        
                        if 'message' in update and 'text' in update['message']:
                            text = update['message']['text']
                            chat_id = update['message']['chat']['id']
                            message_time = update['message'].get('date', time.time())
                            
                            # Проверяем, что сообщение не старше 5 минут
                            current_time = time.time()
                            if current_time - message_time > 300:  # 5 минут
                                print(f"⚠️ Пропускаем старое сообщение: {text}")
                                continue
                            
                            if str(chat_id) == self.chat_id:
                                self.commands_handler.process_command(text, bot_instance)
            
        except Exception as e:
            print(f"❌ Ошибка проверки Telegram команд: {e}")

    def cleanup(self):
        """🧹 ОЧИСТКА РЕСУРСОВ"""
        if hasattr(self.commands_handler, 'cleanup'):
            self.commands_handler.cleanup()
