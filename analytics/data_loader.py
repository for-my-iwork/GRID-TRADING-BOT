# analytics/data_loader.py
"""
📥 МОДУЛЬ ЗАГРУЗКИ И СОХРАНЕНИЯ ИСТОРИЧЕСКИХ ДАННЫХ - ИСПРАВЛЕННАЯ ВЕРСИЯ
"""

import pandas as pd
import json
import os
import numpy as np
from datetime import datetime, timedelta
import time
from tqdm import tqdm
from utils.api_client import APIClient

class HistoricalDataLoader:
    """📥 ЗАГРУЗЧИК ИСТОРИЧЕСКИХ ДАННЫХ С СОХРАНЕНИЕМ В CSV/JSON"""
    
    def __init__(self, symbol="BTCUSDT", data_dir="historical_data"):
        self.symbol = symbol
        self.data_dir = data_dir
        self.api_client = APIClient()
        
        # Создаем директории для данных
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(f"{data_dir}/csv", exist_ok=True)
        os.makedirs(f"{data_dir}/json", exist_ok=True)

    def load_and_save_data(self, days=30, interval="5", force_reload=False):
        """
        📥 ЗАГРУЗКА И СОХРАНЕНИЕ ДАННЫХ В CSV И JSON
        
        Args:
            days: Количество дней для загрузки
            interval: Интервал данных (1, 5, 15, 60, ...)
            force_reload: Принудительная перезагрузка даже если файлы существуют
        """
        filename_base = f"{self.symbol}_{interval}m_{days}days"
        csv_path = f"{self.data_dir}/csv/{filename_base}.csv"
        json_path = f"{self.data_dir}/json/{filename_base}.json"
        
        # Проверяем, есть ли уже сохраненные данные
        if not force_reload and os.path.exists(csv_path) and os.path.exists(json_path):
            print(f"📁 Загружаем данные из файлов...")
            data = self._load_from_files(csv_path, json_path)
            
            # Проверяем целостность загруженных данных
            if not data.empty:
                data = self._validate_and_repair_data(data, days, interval, csv_path, json_path)
            
            return data
        
        print(f"📥 Загрузка новых данных: {days} дней, интервал {interval} минут")
        data = self._fetch_historical_data(days, interval)
        
        if data.empty:
            print("❌ Не удалось загрузить данные")
            return pd.DataFrame()
        
        # Проверяем и восстанавливаем целостность данных
        data = self._validate_and_repair_data(data, days, interval, csv_path, json_path)
        
        # Сохраняем в CSV
        self._save_to_csv(data, csv_path)
        
        # Сохраняем в JSON
        self._save_to_json(data, json_path)
        
        print(f"✅ Данные сохранены:")
        print(f"   📊 CSV: {csv_path}")
        print(f"   📁 JSON: {json_path}")
        print(f"   📈 Записей: {len(data)}")
        print(f"   📅 Период: {data.index[0]} - {data.index[-1]}")
        
        return data

    def _validate_and_repair_data(self, data, days, interval, csv_path, json_path):
        """🔍 ПРОВЕРКА И ВОССТАНОВЛЕНИЕ ЦЕЛОСТНОСТИ ДАННЫХ"""
        print("🔍 Проверка целостности данных...")
        
        initial_count = len(data)
        issues_found = 0
        
        # Проверяем пропущенные значения в основных колонках
        essential_columns = ['open', 'high', 'low', 'close', 'volume']
        for column in essential_columns:
            missing_count = data[column].isna().sum()
            if missing_count > 0:
                print(f"⚠️  Найдено {missing_count} пропущенных значений в {column}")
                issues_found += missing_count
        
        # Проверяем целостность временного ряда
        expected_freq = f"{interval}min"
        time_diffs = data.index.to_series().diff()
        expected_diff = pd.Timedelta(minutes=int(interval))
        
        gaps = time_diffs[time_diffs > expected_diff * 1.1]  # 10% допуск
        if not gaps.empty:
            print(f"⚠️  Найдено {len(gaps)} временных разрывов в данных")
            issues_found += len(gaps)
            
            # Показываем первые 3 разрыва
            for i, (idx, gap) in enumerate(gaps.head(3).items()):
                print(f"   - Разрыв {i+1}: {time_diffs[idx]} в {idx}")
        
        # Проверяем технические индикаторы
        indicator_columns = ['sma_20', 'sma_50', 'rsi_14', 'atr_14', 'volume_sma_20']
        for column in indicator_columns:
            if column in data.columns:
                missing_indicators = data[column].isna().sum()
                if missing_indicators > 0:
                    print(f"ℹ️  {missing_indicators} пропущенных значений в {column} (ожидаемо для начальных данных)")
        
        if issues_found > 0:
            print(f"🔄 Восстановление {issues_found} проблемных записей...")
            data = self._repair_missing_data(data, days, interval)
            
            # Пересчитываем технические индикаторы
            data = self._calculate_technical_indicators(data)
            
            print(f"✅ Восстановлено {initial_count - len(data)} записей")
        
        return data

    def _repair_missing_data(self, data, days, interval):
        """🔧 ВОССТАНОВЛЕНИЕ ПРОПУЩЕННЫХ ДАННЫХ"""
        print("🔄 Поиск и восстановление пропущенных данных...")
        
        # Создаем полный временной индекс
        start_time = data.index.min()
        end_time = data.index.max()
        full_index = pd.date_range(start=start_time, end=end_time, freq=f'{interval}min')  # Исправлено
        
        # Реиндексируем данные
        data = data.reindex(full_index)
        
        # Восстанавливаем пропущенные основные данные
        essential_columns = ['open', 'high', 'low', 'close', 'volume', 'turnover']
        
        for column in essential_columns:
            if column in data.columns:
                # Интерполяция для числовых колонок
                if column in ['volume', 'turnover']:
                    data[column] = data[column].fillna(0)
                else:
                    # Для ценовых данных используем forward fill + backward fill
                    # Исправление метода fillna
                    data[column] = data[column].ffill().bfill()
        
        # Удаляем строки, которые не удалось восстановить
        data = data.dropna(subset=essential_columns)
        
        return data

    def _fetch_historical_data(self, days, interval):
        """📡 ЗАГРУЗКА ДАННЫХ С API BYBIT"""
        print(f"📡 Загрузка {interval}-минутных данных за {days} дней...")
        
        end_time = int(datetime.now().timestamp() * 1000)
        start_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
        
        all_data = []
        current_start = start_time
        
        # Расчет общего количества запросов для прогресс-бара
        interval_ms = int(interval) * 60 * 1000
        total_candles = (end_time - start_time) // interval_ms
        total_requests = (total_candles + 199) // 200  # 200 свечей на запрос
        
        successful_requests = 0
        failed_requests = 0
        
        with tqdm(total=total_requests, desc="📊 Загрузка данных") as pbar:
            while current_start < end_time:
                try:
                    time.sleep(0.3)  # Ограничение скорости API
                    
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
                            
                        # Обрабатываем данные
                        batch_data = []
                        for candle in kline_data:
                            try:
                                batch_data.append({
                                    'timestamp': datetime.fromtimestamp(int(candle[0]) / 1000),
                                    'open': float(candle[1]),
                                    'high': float(candle[2]),
                                    'low': float(candle[3]),
                                    'close': float(candle[4]),
                                    'volume': float(candle[5]),
                                    'turnover': float(candle[6]) if len(candle) > 6 else 0
                                })
                            except (ValueError, IndexError) as e:
                                print(f"⚠️ Ошибка обработки свечи: {e}")
                                continue
                        
                        all_data.extend(batch_data)
                        successful_requests += 1
                        
                        # Обновляем временную метку
                        last_timestamp = int(kline_data[-1][0])
                        current_start = last_timestamp + interval_ms
                        
                        pbar.update(1)
                        pbar.set_postfix({
                            'Успешно': successful_requests,
                            'Ошибки': failed_requests,
                            'Свечей': len(all_data),
                            'Дата': datetime.fromtimestamp(last_timestamp/1000).strftime('%Y-%m-%d %H:%M')
                        })
                        
                        if last_timestamp >= end_time:
                            break
                    else:
                        error_msg = response.get('retMsg', 'Unknown error') if response else 'No response'
                        print(f"❌ Ошибка API: {error_msg}")
                        failed_requests += 1
                        break
                        
                except Exception as e:
                    print(f"❌ Ошибка загрузки: {e}")
                    failed_requests += 1
                    # Продолжаем попытки с следующего временного интервала
                    current_start += 200 * interval_ms
                    if failed_requests >= 100:  # Максимум 100 ошибок подряд
                        print("❌ Превышено максимальное количество ошибок. Прерывание загрузки.")
                        break
        
        print(f"📊 Статистика загрузки: {successful_requests} успешных запросов, {failed_requests} ошибок")
        
        if all_data:
            # Создаем DataFrame
            df = pd.DataFrame(all_data)
            df.set_index('timestamp', inplace=True)
            df = df[~df.index.duplicated(keep='first')]
            df.sort_index(inplace=True)
            
            # Добавляем дополнительные вычисляемые поля
            df = self._calculate_technical_indicators(df)
            
            return df
        
        print("❌ Не удалось загрузить ни одной свечи")
        return pd.DataFrame()

    def _calculate_technical_indicators(self, df):
        """📈 ВЫЧИСЛЕНИЕ ТЕХНИЧЕСКИХ ИНДИКАТОРОВ"""
        print("📈 Вычисление технических индикаторов...")
        
        try:
            # SMA
            df['sma_20'] = df['close'].rolling(window=20, min_periods=1).mean()
            df['sma_50'] = df['close'].rolling(window=50, min_periods=1).mean()
            
            # RSI
            df['rsi_14'] = self._calculate_rsi(df['close'], 14)
            
            # ATR (Average True Range) - для волатильности
            df['atr_14'] = self._calculate_atr(df, 14)
            
            # Volume SMA
            df['volume_sma_20'] = df['volume'].rolling(window=20, min_periods=1).mean()
            
            # Процент изменения
            df['price_change_pct'] = df['close'].pct_change() * 100
            
            print("✅ Технические индикаторы вычислены")
            return df
            
        except Exception as e:
            print(f"⚠️ Ошибка вычисления индикаторов: {e}")
            return df

    def _calculate_rsi(self, prices, period=14):
        """📊 ВЫЧИСЛЕНИЕ RSI"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except Exception as e:
            print(f"⚠️ Ошибка вычисления RSI: {e}")
            return pd.Series(index=prices.index, dtype=float)

    def _calculate_atr(self, df, period=14):
        """📏 ВЫЧИСЛЕНИЕ ATR (AVERAGE TRUE RANGE)"""
        try:
            high_low = df['high'] - df['low']
            high_close = abs(df['high'] - df['close'].shift())
            low_close = abs(df['low'] - df['close'].shift())
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(window=period).mean()
            return atr
        except Exception as e:
            print(f"⚠️ Ошибка вычисления ATR: {e}")
            return pd.Series(index=df.index, dtype=float)

    def _save_to_csv(self, data, filepath):
        """💾 СОХРАНЕНИЕ В CSV - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        try:
            # Сохраняем с дополнительной информацией в комментариях
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# Historical Data for {self.symbol}\n")
                f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Period: {data.index[0]} - {data.index[-1]}\n")
                f.write(f"# Records: {len(data)}\n")
                f.write("# Columns: timestamp,open,high,low,close,volume,turnover,sma_20,sma_50,rsi_14,atr_14,volume_sma_20,price_change_pct\n")
            
            # Сохраняем данные (сбрасываем индекс для сохранения timestamp как колонки)
            data_copy = data.copy()
            data_copy = data_copy.replace([np.inf, -np.inf], np.nan)
            
            # Сбрасываем индекс и сохраняем его как колонку
            data_copy.reset_index(inplace=True)
            data_copy.to_csv(filepath, mode='a', index=False, encoding='utf-8', na_rep='')
            print(f"✅ CSV сохранен: {filepath}")
            
        except Exception as e:
            print(f"❌ Ошибка сохранения CSV: {e}")

    def _save_to_json(self, data, filepath):
        """💾 СОХРАНЕНИЕ В JSON"""
        try:
            # Подготавливаем данные для JSON
            json_data = {
                "metadata": {
                    "symbol": self.symbol,
                    "generated": datetime.now().isoformat(),
                    "period_start": data.index[0].isoformat(),
                    "period_end": data.index[-1].isoformat(),
                    "records": len(data),
                    "columns": list(data.columns)
                },
                "data": []
            }
            
            # Конвертируем каждую строку в словарь, заменяя NaN на None
            for timestamp, row in data.iterrows():
                record = {"timestamp": timestamp.isoformat()}
                row_dict = row.to_dict()
                
                # Заменяем NaN на None для корректной JSON сериализации
                for key, value in row_dict.items():
                    if pd.isna(value):
                        row_dict[key] = None
                
                record.update(row_dict)
                json_data["data"].append(record)
            
            # Сохраняем JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False, default=self._json_serializer)
                
            print(f"✅ JSON сохранен: {filepath}")
            
        except Exception as e:
            print(f"❌ Ошибка сохранения JSON: {e}")

    def _json_serializer(self, obj):
        """🔧 СЕРИАЛИЗАТОР ДЛЯ JSON ДЛЯ ОБРАБОТКИ SPECIAL TYPES"""
        if isinstance(obj, (np.float32, np.float64)):
            return float(obj) if not np.isnan(obj) else None
        if isinstance(obj, (np.int32, np.int64)):
            return int(obj)
        if pd.isna(obj):
            return None
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    def _load_from_files(self, csv_path, json_path):
        """📁 ЗАГРУЗКА ДАННЫХ ИЗ ФАЙЛОВ - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        try:
            print(f"📁 Загрузка данных из {csv_path}...")
            
            # Сначала пробуем загрузить с именованным индексом
            try:
                df = pd.read_csv(
                    csv_path, 
                    comment='#', 
                    index_col='timestamp', 
                    parse_dates=True,
                    encoding='utf-8'
                )
            except (KeyError, ValueError):
                # Fallback: загружаем без индекса и устанавливаем вручную
                print("⚠️  Заголовок 'timestamp' не найден, пытаемся восстановить...")
                df = pd.read_csv(csv_path, comment='#', encoding='utf-8')
                
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    df.set_index('timestamp', inplace=True)
                elif 'Unnamed: 0' in df.columns:
                    # Старый формат без названия колонки
                    df.rename(columns={'Unnamed: 0': 'timestamp'}, inplace=True)
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    df.set_index('timestamp', inplace=True)
                else:
                    # Создаем искусственный индекс
                    print("⚠️  Создаем искусственный временной индекс...")
                    df.index = pd.date_range(
                        start=datetime.now() - timedelta(days=30),
                        periods=len(df),
                        freq='5min'
                    )
                    df.index.name = 'timestamp'
            
            # Убедимся, что индекс отсортирован
            df.sort_index(inplace=True)
            
            # Загружаем метаданные из JSON
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                
                print(f"✅ Данные загружены из файлов:")
                print(f"   📊 Записей: {len(df)}")
                print(f"   📅 Период: {df.index[0]} - {df.index[-1]}")
                
                # Восстанавливаем типы данных из метаданных если нужно
                if 'metadata' in json_data:
                    metadata = json_data['metadata']
                    print(f"   📁 Набор: {metadata.get('symbol', 'unknown')} - {metadata.get('records', 0)} записей")
            else:
                print(f"✅ CSV загружен (JSON не найден): {len(df)} записей")
            
            return df
            
        except Exception as e:
            print(f"❌ Ошибка загрузки из файлов: {e}")
            import traceback
            print(f"Детали ошибки: {traceback.format_exc()}")
            return pd.DataFrame()

    def get_available_datasets(self):
        """📋 ПОЛУЧЕНИЕ СПИСКА ДОСТУПНЫХ НАБОРОВ ДАННЫХ"""
        datasets = []
        
        for file in os.listdir(f"{self.data_dir}/csv"):
            if file.endswith('.csv'):
                datasets.append(file.replace('.csv', ''))
        
        return sorted(datasets)

    def load_specific_dataset(self, dataset_name):
        """📁 ЗАГРУЗКА КОНКРЕТНОГО НАБОРА ДАННЫХ"""
        csv_path = f"{self.data_dir}/csv/{dataset_name}.csv"
        json_path = f"{self.data_dir}/json/{dataset_name}.json"
        
        if os.path.exists(csv_path):
            data = self._load_from_files(csv_path, json_path)
            
            # Определяем параметры из имени файла для валидации
            if not data.empty:
                try:
                    parts = dataset_name.split('_')
                    if len(parts) >= 3:
                        interval = parts[1].replace('m', '')
                        days = int(parts[2].replace('days', ''))
                        data = self._validate_and_repair_data(data, days, interval, csv_path, json_path)
                except (ValueError, IndexError):
                    print("⚠️ Не удалось определить параметры набора данных")
                    
            return data
        else:
            print(f"❌ Набор данных '{dataset_name}' не найден")
            return pd.DataFrame()
