# GRID-TRADING-BOT

# 1. Создать окружение
python3 -m venv grid_bot_env

# 2. Активировать
# Windows:
grid_bot_env\Scripts\activate
# Linux/Mac:
source grid_bot_env/bin/activate

# 3. Установить зависимости
pip install pybit requests numpy python-dotenv argparse pandas tqdm

Способ 1: Перенаправление вывода через systemd (рекомендую)
Измените ваш service файл:

bash
sudo nano /etc/systemd/system/grid-bot.service
Замените секцию [Service] на:

ini
[Service]
Type=simple
User=test-bot
Group=test-bot
WorkingDirectory=/home/test-bot/GRID-TRADING-BOT-dev
Environment=PYTHONUNBUFFERED=1
ExecStart=/bin/bash -c "/home/test-bot/GRID-TRADING-BOT-dev/grid_bot_env/bin/python /home/test-bot/GRID-TRADING-BOT-dev/main.py >> /home/test-bot/GRID-TRADING-BOT-dev/logs/bot.log 2>&1"
ExecStop=/bin/kill -SIGTERM $MAINPID
Restart=always
RestartSec=10
SyslogIdentifier=grid-bot-test

# Ограничения для безопасности
MemoryLimit=512M
CPUQuota=100%
Затем выполните:

bash
# Создаем папку для логов
mkdir -p /home/test-bot/GRID-TRADING-BOT-dev/logs

# Даем права
sudo chown test-bot:test-bot /home/test-bot/GRID-TRADING-BOT-dev/logs

# Перезагружаем службу
sudo systemctl daemon-reload
sudo systemctl restart grid-bot.service

Способ 3: Использование tee для дублирования вывода
Если хотите видеть вывод И в журнал И в файл:

ini
ExecStart=/bin/bash -c "/home/test-bot/GRID-TRADING-BOT-dev/grid_bot_env/bin/python /home/test-bot/GRID-TRADING-BOT-dev/main.py 2>&1 | tee -a /home/test-bot/GRID-TRADING-BOT-dev/logs/bot.log"
Проверка
После настройки:

bash
# Следим за логом в реальном времени
tail -f /home/test-bot/GRID-TRADING-BOT-dev/logs/bot.log

# Или следим за службой
sudo journalctl -u grid-bot.service -f

Несколько полезных команд для работы с логами:
bash
# Просмотр лога в реальном времени
tail -f /home/test-bot/GRID-TRADING-BOT-dev/logs/bot.log

# Просмотр последних 100 строк
tail -n 100 /home/test-bot/GRID-TRADING-BOT-dev/logs/bot.log

# Поиск ошибок в логе
grep -i "error\|exception\|fail" /home/test-bot/GRID-TRADING-BOT-dev/logs/bot.log

# Размер лог-файла
ls -lh /home/test-bot/GRID-TRADING-BOT-dev/logs/bot.log

# 4. Загрузка данных для симулятора
python3 data_loader_cli.py --days 1 --interval 1 --force-reload
после days - дни
после интервала - 1/5/30 минутные тренды

# 5. Запуск симулятора
python3 simulator_cli.py --days 7 --usdt 50000 --btc 1

