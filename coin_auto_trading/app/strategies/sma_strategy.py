"""
SMA 크로스 전략
"""
from app.strategies.base_strategy import BaseStrategy
from app.data.candle import Candle, Timeframe
from app.core.state_machine import PositionState
from app.features.indicators import calculate_features
from typing import Dict, Optional, List


class SMAStrategy(BaseStrategy):
    """SMA 크로스 전략 (골든크로스/데드크로스)"""
    
    def __init__(self, fast_period: int = 5, slow_period: int = 20):
        """
        초기화
        
        Parameters
        ----------
        fast_period : int
            빠른 SMA 기간
        slow_period : int
            느린 SMA 기간
        """
        super().__init__(f"SMA_{fast_period}_{slow_period}")
        self.fast_period = fast_period
        self.slow_period = slow_period
    
    def generate_signal(self, candles: Dict[Timeframe, List[Candle]], 
                       current_state: PositionState,
                       features: Optional[Dict] = None) -> Dict:
        """
        SMA 크로스 시그널 생성
        """
        # 기본 타임프레임 사용 (15분 또는 첫 번째 타임프레임)
        timeframe = Timeframe.MIN_15
        if timeframe not in candles or not candles[timeframe]:
            return {
                'action': 'HOLD',
                'confidence': 0.0,
                'reason': 'No candle data',
                'metadata': {}
            }
        
        candle_list = candles[timeframe]
        if len(candle_list) < self.slow_period:
            return {
                'action': 'HOLD',
                'confidence': 0.0,
                'reason': 'Insufficient data',
                'metadata': {}
            }
        
        # 피처 계산
        if features is None:
            features = calculate_features(candle_list)
        
        fast_key = f'sma_{self.fast_period}'
        slow_key = f'sma_{self.slow_period}'
        
        fast_sma = features.get(fast_key, [])
        slow_sma = features.get(slow_key, [])
        
        if not fast_sma or not slow_sma:
            # SMA가 없으면 계산
            from app.features.indicators import sma
            closes = [c.close for c in candle_list]
            fast_sma = sma(closes, self.fast_period)
            slow_sma = sma(closes, self.slow_period)
        
        # 최신 2개 값 비교 (크로스 확인)
        if len(fast_sma) < 2 or len(slow_sma) < 2:
            return {
                'action': 'HOLD',
                'confidence': 0.0,
                'reason': 'Insufficient SMA data',
                'metadata': {}
            }
        
        fast_prev = fast_sma[-2]
        fast_curr = fast_sma[-1]
        slow_prev = slow_sma[-2]
        slow_curr = slow_sma[-1]
        
        if fast_prev is None or fast_curr is None or slow_prev is None or slow_curr is None:
            return {
                'action': 'HOLD',
                'confidence': 0.0,
                'reason': 'SMA values are None',
                'metadata': {}
            }
        
        # 골든크로스: 빠른 SMA가 느린 SMA를 위로 돌파
        golden_cross = fast_prev <= slow_prev and fast_curr > slow_curr
        
        # 데드크로스: 빠른 SMA가 느린 SMA를 아래로 돌파
        dead_cross = fast_prev >= slow_prev and fast_curr < slow_curr
        
        current_price = candle_list[-1].close
        
        if golden_cross and current_state == PositionState.FLAT:
            return {
                'action': 'BUY',
                'confidence': 0.7,
                'reason': f'Golden cross: SMA{self.fast_period} crossed above SMA{self.slow_period}',
                'metadata': {
                    'fast_sma': fast_curr,
                    'slow_sma': slow_curr,
                    'price': current_price
                }
            }
        
        elif dead_cross and current_state == PositionState.LONG:
            return {
                'action': 'SELL',
                'confidence': 0.7,
                'reason': f'Dead cross: SMA{self.fast_period} crossed below SMA{self.slow_period}',
                'metadata': {
                    'fast_sma': fast_curr,
                    'slow_sma': slow_curr,
                    'price': current_price
                }
            }
        
        return {
            'action': 'HOLD',
            'confidence': 0.0,
            'reason': 'No signal',
            'metadata': {
                'fast_sma': fast_curr,
                'slow_sma': slow_curr
            }
        }
    
    def get_required_timeframes(self) -> List[Timeframe]:
        """필요한 타임프레임"""
        return [Timeframe.MIN_15]

