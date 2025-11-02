# ai/market_analyzer.py
"""
🧠 АНАЛИЗ РЫНКА ДЛЯ AI ОПТИМИЗАЦИИ
"""

import numpy as np
from config import DEMO_MODE

class MarketAnalyzer:
    """🧠 АНАЛИЗ РЫНКА ДЛЯ AI ОПТИМИЗАЦИИ"""
    
    def __init__(self, api_client):
        self.api_client = api_client
        self.is_analyzing = False

    def multi_timeframe_analysis(self, symbol, price_history):
        """📈 МУЛЬТИТАЙМФРЕЙМНЫЙ АНАЛИЗ РЫНКА"""
        if self.is_analyzing:
            return self.get_fallback_analysis()
        
        self.is_analyzing = True
        try:
            if DEMO_MODE:
                current_trend = self.analyze_trend_demo(price_history)
                current_volatility = self.calculate_volatility_demo(price_history)
                
                analysis = {
                    'trend_1': current_trend,
                    'trend_5': current_trend, 
                    'trend_15': current_trend,
                    'trend_60': current_trend,
                    'volatility_1': current_volatility,
                    'volatility_5': current_volatility,
                    'support_resistance': self.find_support_resistance_demo(price_history),
                    'market_regime': self.determine_market_regime_demo(current_volatility, current_trend)
                }
                return analysis
            else:
                # Реальный режим (будет работать когда DEMO_MODE = False)
                analysis = {
                    'trend_1': self.analyze_trend(symbol, '1'),
                    'trend_5': self.analyze_trend(symbol, '5'), 
                    'trend_15': self.analyze_trend(symbol, '15'),
                    'trend_60': self.analyze_trend(symbol, '60'),
                    'volatility_1': self.calculate_timeframe_volatility(symbol, '1'),
                    'volatility_5': self.calculate_timeframe_volatility(symbol, '5'),
                    'support_resistance': self.find_support_resistance(symbol),
                    'market_regime': self.determine_market_regime(symbol)
                }
                return analysis
        finally:
            self.is_analyzing = False

    def get_fallback_analysis(self):
        """🔄 РЕЗЕРВНЫЙ АНАЛИЗ ПРИ ОШИБКАХ"""
        return {
            'trend_1': 'neutral',
            'trend_5': 'neutral', 
            'trend_15': 'neutral',
            'trend_60': 'neutral',
            'volatility_1': 0.001,
            'volatility_5': 0.001,
            'support_resistance': {'support': 0, 'resistance': 0, 'current_vs_support': 0, 'current_vs_resistance': 0},
            'market_regime': 'normal_volatility'
        }

    def analyze_trend_demo(self, price_history):
        """📊 АНАЛИЗ ТРЕНДА ДЛЯ ДЕМО-РЕЖИМА"""
        try:
            if len(price_history) < 20:
                return "unknown"
            
            recent_prices = price_history[-20:]
            first_half = sum(recent_prices[:10]) / 10
            second_half = sum(recent_prices[10:]) / 10
            
            change_pct = ((second_half - first_half) / first_half) * 100
            
            if change_pct > 0.1:
                return "bullish"
            elif change_pct < -0.1:
                return "bearish"
            else:
                return "neutral"
        except Exception as e:
            print(f"❌ Ошибка анализа тренда (демо): {e}")
            return "unknown"

    def calculate_volatility_demo(self, price_history):
        """📏 РАСЧЕТ ВОЛАТИЛЬНОСТИ ДЛЯ ДЕМО-РЕЖИМА"""
        try:
            if len(price_history) < 20:
                return 0.001
            
            prices = price_history[-50:]
            if len(prices) < 10:
                return 0.001
                
            returns = np.diff(np.log(prices))
            volatility = np.std(returns) * np.sqrt(365 * 24 * 60)
            return max(0.001, min(0.05, volatility))
        except Exception as e:
            print(f"❌ Ошибка расчета волатильности (демо): {e}")
            return 0.001

    def find_support_resistance_demo(self, price_history):
        """🎯 УРОВНИ ПОДДЕРЖКИ/СОПРОТИВЛЕНИЯ ДЛЯ ДЕМО-РЕЖИМА"""
        try:
            if len(price_history) == 0:
                return {'support': 0, 'resistance': 0, 'current_vs_support': 0, 'current_vs_resistance': 0}
            
            current_price = price_history[-1]
            support = current_price * 0.99
            resistance = current_price * 1.01
            
            return {
                'support': support,
                'resistance': resistance,
                'current_vs_support': (current_price - support) / support * 100,
                'current_vs_resistance': (current_price - resistance) / resistance * 100
            }
        except Exception as e:
            print(f"❌ Ошибка поиска уровней (демо): {e}")
            return {'support': 0, 'resistance': 0, 'current_vs_support': 0, 'current_vs_resistance': 0}

    def determine_market_regime_demo(self, volatility, trend):
        """🎪 ОПРЕДЕЛЕНИЕ РЕЖИМА РЫНКА ДЛЯ ДЕМО-РЕЖИМА"""
        try:
            if volatility > 0.02:
                return "high_volatility"
            elif volatility < 0.005:
                return "low_volatility"
            else:
                return "normal_volatility"
        except Exception as e:
            print(f"❌ Ошибка определения режима рынка (демо): {e}")
            return "unknown"

    def analyze_trend(self, symbol, timeframe='5'):
        """📊 АНАЛИЗ ТРЕНДА ДЛЯ РЕАЛЬНОГО РЕЖИМА"""
        try:
            klines = self.api_client.robust_api_call(
                self.api_client.session.get_kline,
                category="spot",
                symbol=symbol,
                interval=timeframe,
                limit=50
            )
            
            if klines and 'result' in klines and 'list' in klines['result']:
                prices = [float(candle[4]) for candle in klines['result']['list']]
                
                if len(prices) >= 20:
                    sma_short = sum(prices[-10:]) / 10
                    sma_long = sum(prices[-20:]) / 20
                    
                    if sma_short > sma_long * 1.002:
                        return "bullish"
                    elif sma_short < sma_long * 0.998:
                        return "bearish"
                    else:
                        return "neutral"
        
            return "unknown"
        except Exception as e:
            print(f"❌ Ошибка анализа тренда {timeframe}: {e}")
            return "unknown"

    def calculate_timeframe_volatility(self, symbol, timeframe='5'):
        """📏 РАСЧЕТ ВОЛАТИЛЬНОСТИ ДЛЯ РЕАЛЬНОГО РЕЖИМА"""
        try:
            klines = self.api_client.robust_api_call(
                self.api_client.session.get_kline,
                category="spot",
                symbol=symbol,
                interval=timeframe,
                limit=50
            )
            
            if klines and 'result' in klines and 'list' in klines['result']:
                prices = [float(candle[4]) for candle in klines['result']['list']]
                
                if len(prices) >= 20:
                    returns = np.diff(np.log(prices))
                    volatility = np.std(returns) * np.sqrt(365 * 24 * 60)
                    return max(0.001, min(0.05, volatility))
            
            return 0.001
        except Exception as e:
            print(f"❌ Ошибка расчета волатильности {timeframe}: {e}")
            return 0.001

    def find_support_resistance(self, symbol):
        """🎯 УРОВНИ ПОДДЕРЖКИ/СОПРОТИВЛЕНИЯ ДЛЯ РЕАЛЬНОГО РЕЖИМА"""
        try:
            klines = self.api_client.robust_api_call(
                self.api_client.session.get_kline,
                category="spot",
                symbol=symbol,
                interval='60',
                limit=100
            )
            
            if klines and 'result' in klines and 'list' in klines['result']:
                prices = [float(candle[4]) for candle in klines['result']['list']]
                
                if len(prices) >= 20:
                    recent_low = min(prices[-10:])
                    recent_high = max(prices[-10:])
                    current_price = prices[-1]
                    
                    return {
                        'support': recent_low,
                        'resistance': recent_high,
                        'current_vs_support': (current_price - recent_low) / recent_low * 100,
                        'current_vs_resistance': (current_price - recent_high) / recent_high * 100
                    }
            
            return {'support': 0, 'resistance': 0, 'current_vs_support': 0, 'current_vs_resistance': 0}
        except Exception as e:
            print(f"❌ Ошибка поиска уровней поддержки/сопротивления: {e}")
            return {'support': 0, 'resistance': 0, 'current_vs_support': 0, 'current_vs_resistance': 0}

    def determine_market_regime(self, symbol):
        """🎪 ОПРЕДЕЛЕНИЕ РЕЖИМА РЫНКА ДЛЯ РЕАЛЬНОГО РЕЖИМА"""
        try:
            analysis = self.multi_timeframe_analysis(symbol, [])
            
            trends = [analysis['trend_1'], analysis['trend_5'], analysis['trend_15']]
            bull_count = trends.count('bullish')
            bear_count = trends.count('bearish')
            
            if bull_count >= 2:
                return "strong_bull"
            elif bear_count >= 2:
                return "strong_bear" 
            else:
                avg_volatility = (analysis['volatility_1'] + analysis['volatility_5']) / 2
                if avg_volatility < 0.008:
                    return "consolidation_low"
                else:
                    return "consolidation_high"
        except Exception as e:
            print(f"❌ Ошибка определения режима рынка: {e}")
            return "unknown"
