#!/usr/bin/env python3
# data_loader_cli.py
"""
📥 КОМАНДНАЯ СТРОКА ДЛЯ ЗАГРУЗКИ ДАННЫХ
"""

import argparse
from analytics.data_loader import HistoricalDataLoader

def main():
    parser = argparse.ArgumentParser(description='Загрузчик исторических данных Bybit')
    parser.add_argument('--days', type=int, default=30, help='Количество дней для загрузки')
    parser.add_argument('--interval', type=str, default='5', help='Интервал данных (1, 5, 15, 60)')
    parser.add_argument('--symbol', type=str, default='BTCUSDT', help='Торговая пара')
    parser.add_argument('--force-reload', action='store_true', help='Принудительная перезагрузка')
    
    args = parser.parse_args()
    
    print("📥 ЗАГРУЗЧИК ИСТОРИЧЕСКИХ ДАННЫХ")
    print("=" * 50)
    
    loader = HistoricalDataLoader(symbol=args.symbol)
    data = loader.load_and_save_data(
        days=args.days,
        interval=args.interval,
        force_reload=args.force_reload
    )
    
    if not data.empty:
        print(f"✅ УСПЕХ! Загружено {len(data)} записей")
        
        # Показываем доступные наборы
        datasets = loader.get_available_datasets()
        if datasets:
            print(f"\n📁 Доступные наборы данных:")
            for dataset in datasets[-5:]:  # Последние 5
                print(f"   • {dataset}")
    else:
        print("❌ Не удалось загрузить данные")

if __name__ == "__main__":
    main()
