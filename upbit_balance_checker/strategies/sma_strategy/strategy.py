"""
SMA 골든크로스 전략 구현

단순 이동평균선의 크로스를 이용한 매매 전략
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path

# 상위 디렉토리의 모듈 import를 위한 경로 추가
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.indicators import calculate_sma


class SMAStrategy:
    """
    SMA 골든크로스 전략
    
    - 골든크로스: 매수 신호
    - 데드크로스: 매도 신호
    """
    
    def __init__(self, fast_period: int = 5, slow_period: int = 30):
        """
        Parameters
        ----------
        fast_period : int
            단기 이동평균 기간
        slow_period : int
            장기 이동평균 기간
        """
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.name = f"SMA {fast_period}/{slow_period} 골든크로스"
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        매매 신호 생성
        
        Parameters
        ----------
        df : pd.DataFrame
            가격 데이터 ('종가' 컬럼 필요)
        
        Returns
        -------
        pd.DataFrame
            매매 신호 ('signal'와 'position' 컬럼 포함)
        """
        # 이동평균선 계산
        df_copy = df.copy()
        df_copy['SMA_fast'] = calculate_sma(df_copy, column='종가', window=self.fast_period)
        df_copy['SMA_slow'] = calculate_sma(df_copy, column='종가', window=self.slow_period)
        
        # 크로스 감지
        golden_cross = (
            (df_copy['SMA_fast'].shift(1) < df_copy['SMA_slow'].shift(1)) & 
            (df_copy['SMA_fast'] > df_copy['SMA_slow'])
        )
        dead_cross = (
            (df_copy['SMA_fast'].shift(1) > df_copy['SMA_slow'].shift(1)) & 
            (df_copy['SMA_fast'] < df_copy['SMA_slow'])
        )
        
        # 신호 생성
        signals = pd.DataFrame(index=df_copy.index)
        signals['signal'] = 'HOLD'
        signals.loc[golden_cross, 'signal'] = 'BUY'
        signals.loc[dead_cross, 'signal'] = 'SELL'
        
        # 포지션 생성 (1: 매수, -1: 매도, 0: 홀드)
        signals['position'] = 0
        signals.loc[golden_cross, 'position'] = 1
        signals.loc[dead_cross, 'position'] = -1
        
        return signals
    
    def get_statistics(self, df: pd.DataFrame) -> dict:
        """
        전략 통계 반환
        
        Parameters
        ----------
        df : pd.DataFrame
            가격 데이터
        
        Returns
        -------
        dict
            전략 통계
        """
        df_copy = df.copy()
        df_copy['SMA_fast'] = calculate_sma(df_copy, column='종가', window=self.fast_period)
        df_copy['SMA_slow'] = calculate_sma(df_copy, column='종가', window=self.slow_period)
        
        golden_crosses = (
            (df_copy['SMA_fast'].shift(1) < df_copy['SMA_slow'].shift(1)) & 
            (df_copy['SMA_fast'] > df_copy['SMA_slow'])
        )
        dead_crosses = (
            (df_copy['SMA_fast'].shift(1) > df_copy['SMA_slow'].shift(1)) & 
            (df_copy['SMA_fast'] < df_copy['SMA_slow'])
        )
        
        return {
            'strategy_name': self.name,
            'golden_cross_count': golden_crosses.sum(),
            'dead_cross_count': dead_crosses.sum(),
            'total_crosses': golden_crosses.sum() + dead_crosses.sum()
        }

