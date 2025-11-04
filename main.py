# main.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
"""
🚀 ADVANCED GRID TRADING BOT v9.0
Главный запускающий файл
"""

from core.grid_bot import AdvancedGridBotV90
import warnings
warnings.filterwarnings('ignore')

def main():
    """🚀 ГЛАВНАЯ ФУНКЦИЯ ДЛЯ ЗАПУСКА БОТА"""
    print("🚀 Запуск AI-УЛУЧШЕННОГО Grid Bot v9.0...")
    print("=" * 50)
    
    bot = AdvancedGridBotV90()
    
    if bot.interactive_setup():
        try:
            profit, stopped = bot.run_ai_enhanced_monitoring()
            
            if stopped:
                if hasattr(bot, 'max_api_errors') and bot.api_errors >= bot.max_api_errors:
                    print("\n🛑 Работа остановлена из-за большого количества ошибок API!")
                elif bot.user_commanded_stop:
                    print("\n🛑 Работа остановлена по команде пользователя!")
                elif bot.user_commanded_emergency_stop:
                    print("\n🛑 Аварийная остановка по команде пользователя!")
                else:
                    print("\n🛑 Работа остановлена по условию стоп-лосса!")
            else:
                print("\n🛑 Завершение работы по таймеру...")
            
            if profit > 0:
                print(f"🎉 Бот ЗАРАБОТАЛ: +{profit:.4f} USDT!")
            else:
                print(f"📉 Бот в минусе: {profit:.4f} USDT")
                
        except KeyboardInterrupt:
            print(f"\n\n⏹️  Прервано пользователем")
            try:
                bot.send_telegram_message("🛑 Бот остановлен пользователем")
            except:
                print("⚠️ Не удалось отправить сообщение в Telegram")
            try:
                bot.cancel_all_orders_safe()
            except:
                pass
        except Exception as e:
            print(f"💥 Критическая ошибка: {e}")
            try:
                # Используем существующий метод через telegram_bot
                bot.telegram_bot.send_message(f"💥 Критическая ошибка: {e}")
            except:
                print("⚠️ Не удалось отправить сообщение в Telegram")
            try:
                bot.cancel_all_orders_safe()
            except:
                pass
    else:
        print("❌ Запуск отменен пользователем.")

if __name__ == "__main__":
    main()
