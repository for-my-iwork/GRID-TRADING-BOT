# main.py - ИСПРАВЛЕННАЯ ВЕРСИЯ С АВТОКОНФИГОМ
"""
🚀 ADVANCED GRID TRADING BOT v9.2
Главный запускающий файл
"""

from core.grid_bot import AdvancedGridBot
from analytics.logger import clear_state
import warnings
import signal
import sys
import atexit
import os

warnings.filterwarnings('ignore')

# Проверяем наличие конфига автостарта
AUTO_CONFIG_EXISTS = os.path.exists('auto_config.py')

if AUTO_CONFIG_EXISTS:
    from auto_config import AUTO_START, AUTO_MODE, AUTO_DURATION, AI_GRID_LEVELS, AI_GRID_SPACING, AI_GRID_REFRESH

def save_auto_config(mode, duration, grid_levels=None, grid_spacing=None, grid_refresh=None):
    """💾 СОХРАНЕНИЕ НАСТРОЕК ДЛЯ АВТОМАТИЧЕСКОГО ЗАПУСКА"""
    try:
        with open('auto_config.py', 'w', encoding='utf-8') as f:
            f.write('# auto_config.py\n')
            f.write('"""\n')
            f.write('⚙️ АВТОМАТИЧЕСКАЯ КОНФИГУРАЦИЯ ДЛЯ SYSTEMD\n')
            f.write('"""\n\n')
            f.write('# Автоматический запуск бота\n')
            f.write(f'AUTO_START = True\n')
            f.write(f'AUTO_MODE = {mode}  # 1=стандарт, 2=ручной, 3=AI-режим\n')
            f.write(f'AUTO_DURATION = {duration}  # время работы в минутах\n\n')
            
            if mode == 3 and grid_levels and grid_spacing and grid_refresh:
                f.write('# Дополнительные параметры для AI-режима\n')
                f.write(f'AI_GRID_LEVELS = {grid_levels}\n')
                f.write(f'AI_GRID_SPACING = {grid_spacing}\n')
                f.write(f'AI_GRID_REFRESH = {grid_refresh}\n')
        
        print(f"✅ Настройки сохранены в auto_config.py: режим {mode}, время {duration} мин")
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения конфига: {e}")
        return False

def signal_handler(signum, frame):
    """🔄 ОБРАБОТЧИК СИГНАЛОВ ДЛЯ GRACEFUL SHUTDOWN"""
    print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
    try:
        # Очищаем состояние при принудительном завершении
        clear_state()
    except:
        pass
    sys.exit(0)

def main():
    """🚀 ГЛАВНАЯ ФУНКЦИЯ ДЛЯ ЗАПУСКА БОТА"""
    print("🚀 Запуск AI-УЛУЧШЕННОГО Grid Bot v9.2...")
    print("=" * 50)
    
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    bot = AdvancedGridBot()
    
    # Регистрируем очистку состояния при нормальном завершении
    atexit.register(lambda: clear_state() if not hasattr(bot, 'user_commanded_stop') else None)
    
    # АВТОМАТИЧЕСКИЙ РЕЖИМ ДЛЯ SYSTEMD
    if AUTO_CONFIG_EXISTS and AUTO_START:
        print("🤖 АВТОМАТИЧЕСКИЙ РЕЖИМ ДЛЯ SYSTEMD")
        print(f"📋 Загружены настройки: режим {AUTO_MODE}, время {AUTO_DURATION} мин")
        
        # Устанавливаем параметры из конфига
        bot.ai_mode = True if AUTO_MODE == 3 else False
        bot.monitoring_duration = AUTO_DURATION
        
        # Дополнительные настройки для AI-режима
        if AUTO_MODE == 3:
            bot.grid_levels = AI_GRID_LEVELS
            bot.grid_spacing = AI_GRID_SPACING
            bot.grid_refresh_time = AI_GRID_REFRESH
            print(f"🧠 AI параметры: уровни {AI_GRID_LEVELS}, расстояние {AI_GRID_SPACING*100:.3f}%, обновление {AI_GRID_REFRESH} сек")
        
        print("✅ Параметры установлены из auto_config.py")
        
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
                bot.telegram_bot.send_message(f"💥 Критическая ошибка: {e}")
            except:
                print("⚠️ Не удалось отправить сообщение в Telegram")
            try:
                bot.cancel_all_orders_safe()
            except:
                pass
    
    # ИНТЕРАКТИВНЫЙ РЕЖИМ (для ручного запуска)
    else:
        if bot.interactive_setup():
            # Предлагаем сохранить настройки для автозапуска
            save_config = input("\n💾 Сохранить настройки для автоматического запуска? (y/n): ").strip().lower()
            if save_config == 'y':
                mode = 3 if bot.ai_mode else 1  # Определяем номер режима
                
                # Для AI-режима сохраняем дополнительные параметры
                if bot.ai_mode:
                    save_auto_config(
                        mode=mode,
                        duration=bot.monitoring_duration,
                        grid_levels=bot.grid_levels,
                        grid_spacing=bot.grid_spacing,
                        grid_refresh=bot.grid_refresh_time
                    )
                else:
                    save_auto_config(
                        mode=mode,
                        duration=bot.monitoring_duration
                    )
            
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
