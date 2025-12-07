#!/usr/bin/env python3
# simulator_cli.py
"""
🔁 КОМАНДНАЯ СТРОКА ДЛЯ СИМУЛЯЦИИ ТОРГОВЛИ
"""

import argparse
from analytics.advanced_historical_tester import AdvancedHistoricalTester

def main():
    parser = argparse.ArgumentParser(description='Симулятор торговли AI Grid Bot')
    parser.add_argument('--days', type=int, default=30, help='Дней для тестирования')
    parser.add_argument('--usdt', type=float, default=1000, help='Начальный баланс USDT')
    parser.add_argument('--btc', type=float, default=0.01, help='Начальный баланс BTC')
    parser.add_argument('--no-ai', action='store_true', help='Отключить AI режим')
    parser.add_argument('--dataset', type=str, help='Конкретный набор данных')
    
    args = parser.parse_args()
    
    print("🔁 СИМУЛЯТОР ТОРГОВЛИ AI GRID BOT")
    print("=" * 50)
    
    tester = AdvancedHistoricalTester()
    
    # Если указан конкретный набор данных
    if args.dataset:
        from analytics.data_loader import HistoricalDataLoader
        loader = HistoricalDataLoader()
        data = loader.load_specific_dataset(args.dataset)
        if data.empty:
            print(f"❌ Набор данных '{args.dataset}' не найден")
            return
        
        # Запускаем симуляцию на конкретных данных
        # (здесь нужно будет добавить логику)
        print(f"✅ Загружен набор: {args.dataset}")
    
    # Стандартный полный тест
    results = tester.run_complete_test(
        days=args.days,
        initial_balance=args.usdt,
        initial_btc=args.btc,
        ai_mode=not args.no_ai,
        force_reload=False
    )
    
    if results:
        print("✅ СИМУЛЯЦИЯ ЗАВЕРШЕНА!")
    else:
        print("❌ Симуляция не удалась")

if __name__ == "__main__":
    main()
