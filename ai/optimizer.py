# ai/optimizer.py
"""
🧠 AI ОПТИМИЗАЦИЯ ПАРАМЕТРОВ СЕТКИ
"""

from datetime import datetime
from config import MIN_SESSION_DURATION, MAX_SESSION_DURATION

class AIOptimizer:
    """🧠 AI ОПТИМИЗАЦИЯ ПАРАМЕТРОВ СЕТКИ"""
    def __init__(self, market_analyzer):
        self.market_analyzer = market_analyzer

    def get_optimized_parameters(self, price_history, session_duration):
        """🧠 ПОЛУЧЕНИЕ ОПТИМИЗИРОВАННЫХ ПАРАМЕТРОВ"""
        try:
            market_analysis = self.market_analyzer.multi_timeframe_analysis(
                'BTCUSDT', price_history
            )
            market_regime = market_analysis['market_regime']
            # Оптимизация на основе режима рынка
            if market_regime in ["strong_bull", "high_volatility"]:
                levels = 3
                spacing = 0.002
                grid_refresh = 1800
            elif market_regime in ["strong_bear"]:
                levels = 2
                spacing = 0.0025
                grid_refresh = 1500
            elif market_regime in ["consolidation_low", "low_volatility"]:
                levels = 6
                spacing = 0.001
                grid_refresh = 3600
            else:  # consolidation_high, normal_volatility
                levels = 4
                spacing = 0.0015
                grid_refresh = 2700
            # Оптимизация времени работы
            optimized_duration = self.ai_optimize_session_duration(
                market_regime, session_duration
            )   
            return {
                'grid_levels': levels,
                'grid_spacing': spacing,
                'grid_refresh_time': grid_refresh,
                'session_duration': optimized_duration,
                'market_regime': market_regime,
                'analysis': market_analysis,
                'volatility': market_analysis.get('volatility_1', 0)
            }
        except (ValueError, KeyError, TypeError) as e:
            print(f"❌ Ошибка AI оптимизации: {e}")
            # Возвращаем значения по умолчанию при ошибке
            return {
                'grid_levels': 4,
                'grid_spacing': 0.0015,
                'grid_refresh_time': 1800,
                'session_duration': session_duration,
                'market_regime': 'normal_volatility',
                'analysis': self.market_analyzer.get_fallback_analysis(),
                'volatility': 0.001
            }

    def ai_optimize_session_duration(self, market_regime, requested_duration):
        """⏱️ AI ОПТИМИЗАЦИЯ ВРЕМЕНИ РАБОТЫ СЕССИИ"""
        regime_durations = {
            "strong_bull": 240,
            "strong_bear": 180,
            "consolidation_low": 480,
            "consolidation_high": 360,
            "high_volatility": 180,
            "low_volatility": 480,
            "normal_volatility": 240
        }
        current_hour = datetime.now().hour
        base_duration = regime_durations.get(market_regime, 240)
        # Корректируем длительность сессии в зависимости от времени суток
        if 0 <= current_hour < 5:
            recommended_duration = min(base_duration, 360)
        elif 5 <= current_hour < 13:
            recommended_duration = base_duration
        else:
            recommended_duration = min(base_duration * 1.2, 480)
        # Учитываем запрошенную пользователем длительность, но в пределах разумного
        final_duration = min(requested_duration, recommended_duration)
        final_duration = max(
            MIN_SESSION_DURATION, min(MAX_SESSION_DURATION, final_duration)
        )
        return final_duration
