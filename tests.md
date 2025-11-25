Отлично! Вот полная инструкция для настройки автозапуска и команды для тестирования:

## 🚀 НАСТРОЙКА АВТОЗАПУСКА ДЛЯ ТЕСТОВОГО КОНТУРА

### 1. СОЗДАНИЕ SYSTEMD СЛУЖБЫ

```bash
# Создаем service файл
sudo nano /etc/systemd/system/grid-bot.service
```

**Содержимое файла (адаптируй пути):**
```ini
[Unit]
Description=Grid Trading Bot for Bybit (Test Environment)
After=network.target
Wants=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/GRID-TRADING-BOT
ExecStart=/home/ubuntu/grid_bot_env/bin/python /home/ubuntu/GRID-TRADING-BOT/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=grid-bot-test

# Ограничения для безопасности
MemoryLimit=512M
CPUQuota=100%

[Install]
WantedBy=multi-user.target
```

### 2. АКТИВАЦИЯ И ЗАПУСК СЛУЖБЫ

```bash
# Обновляем systemd
sudo systemctl daemon-reload

# Разрешаем автозапуск при загрузке
sudo systemctl enable grid-bot.service

# Запускаем службу
sudo systemctl start grid-bot.service

# Проверяем статус
sudo systemctl status grid-bot.service
```

### 3. КОМАНДЫ ДЛЯ МОНИТОРИНГА И ТЕСТИРОВАНИЯ

**Мониторинг в реальном времени:**
```bash
# Логи в реальном времени
sudo journalctl -u grid-bot.service -f

# Логи за последний час
sudo journalctl -u grid-bot.service --since "1 hour ago"

# Статус службы
sudo systemctl status grid-bot.service

# Проверка использования памяти
ps aux | grep grid-bot | grep -v grep
```

**Тестовые сценарии State Management:**

```bash
# 1. Тест внезапного отключения
sudo systemctl stop grid-bot.service
# Проверяем что state файл сохранился
ls -la bot_state.json
sudo systemctl start grid-bot.service
sudo journalctl -u grid-bot.service -f

# 2. Тест перезагрузки VPS
sudo reboot
# После перезагрузки проверяем автоматический запуск
sudo systemctl status grid-bot.service

# 3. Тест повреждения state файла
sudo systemctl stop grid-bot.service
echo "corrupted data" > bot_state.json
sudo systemctl start grid-bot.service
# Должен восстановиться из backup или начать заново

# 4. Тест многократного перезапуска
for i in {1..5}; do
    sudo systemctl stop grid-bot.service
    sleep 2
    sudo systemctl start grid-bot.service
    sleep 10
    echo "Cycle $i completed"
done
```

### 4. КОНФИГУРАЦИЯ ДЛЯ НЕДЕЛЬНОГО ТЕСТА

**В config.py установи:**
```python
# Увеличь время работы для недельного теста
MIN_SESSION_DURATION = 60      # 1 час минимум
MAX_SESSION_DURATION = 10080   # 7 дней (10080 минут)

# Настройки для долгой работы
MAX_API_ERRORS = 100           # Больше попыток при долгой работе
TELEGRAM_REPORT_INTERVAL = 3600 # Отчет каждый час
```

**Запусти бота с параметрами для долгого теста:**
```python
# При интерактивной настройке выбери 10080 минут (7 дней)
# Или установи в коде:
self.monitoring_duration = 10080
```

### 5. СКРИПТЫ ДЛЯ АВТОМАТИЧЕСКОГО ТЕСТИРОВАНИЯ

**Создай health-check скрипт:**
```bash
#!/bin/bash
# /home/ubuntu/health_check.sh

SERVICE="grid-bot.service"

if ! systemctl is-active --quiet $SERVICE; then
    echo "❌ Service is not running. Restarting..."
    sudo systemctl restart $SERVICE
    # Отправь уведомление в Telegram
    curl -s -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage" \
        -d chat_id=<YOUR_CHAT_ID> \
        -d text="🔄 Bot restarted automatically"
fi
```

**Добавь в cron для периодической проверки:**
```bash
# Каждые 5 минут проверяем здоровье бота
crontab -e
# Добавь строку:
*/5 * * * * /home/ubuntu/health_check.sh
```

### 6. КОМАНДЫ ДЛЯ ЭКСПЕРИМЕНТОВ С STATE MANAGEMENT

```bash
# Проверка содержимого state файла
cat bot_state.json
jq . bot_state.json  # если установлен jq

# Мониторинг изменений state файла
watch -n 5 'ls -la bot_state.json* && date'

# Создание нагрузки для теста восстановления
while true; do
    sudo systemctl stop grid-bot.service
    sleep 30
    sudo systemctl start grid-bot.service
    sleep 60
done
```

### 7. ВАЖНЫЕ ПРОВЕРКИ ПЕРЕД ЗАПУСКОМ НА НЕДЕЛЮ

1. **Проверь баланс на тестовом контуре** - используй минимальные суммы
2. **Убедись что API ключи тестовые**
3. **Проверь логирование** - папка bot_logs_* создается
4. **Протестируй восстановление** - останови и запусти службу
5. **Проверь телеграм уведомления** - получаешь ли сообщения

### 8. ЭКСТРЕННЫЕ КОМАНДЫ

```bash
# Срочная остановка
sudo systemctl stop grid-bot.service

# Принудительное завершение
sudo pkill -f "python.*main.py"

# Просмотр логов при проблемах
sudo journalctl -u grid-bot.service -n 50 --no-pager

# Очистка состояния (если нужно начать заново)
sudo systemctl stop grid-bot.service
rm -f bot_state.json bot_state.json.backup
sudo systemctl start grid-bot.service
```

Запускай тест и мониторь первые несколько часов. Если всё стабильно - оставляй на неделю! 

**Для нового чата сохрани этот промт - он содержит все команды для управления тестовым запуском.**
