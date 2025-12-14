"""
모멘텀 전략 구현

일정 기간의 수익률(모멘텀)을 계산하여 매매 신호 생성
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path

# 상위 디렉토리의 모듈 import를 위한 경로 추가
sys.path.append(str(Path(__file__).parent.parent.parent))


class MomentumStrategy:
    """
    모멘텀 전략
    
    - 과거 N일간의 수익률(모멘텀) 계산
    - 모멘텀이 임계값 이상: 매수
    - 모멘텀이 임계값 이하: 매도
    """
    
    def __init__(
        self, 
        lookback_period: int = 20,
        buy_threshold: float = 0.05,
        sell_threshold: float = -0.03
    ):
        """
        Parameters
        ----------
        lookback_period : int
            모멘텀 계산 기간 (일)
        buy_threshold : float
            매수 기준 (예: 0.05 = 5% 이상 상승)
        sell_threshold : float
            매도 기준 (예: -0.03 = -3% 이하 하락)
        """
        self.lookback_period = lookback_period
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        self.name = f"{lookback_period}일 모멘텀 전략"
    
    def calculate_momentum(self, df: pd.DataFrame) -> pd.Series:
        """
        모멘텀 계산
        
        Parameters
        ----------
        df : pd.DataFrame
            가격 데이터
        
        Returns
        -------
        pd.Series
            모멘텀 값 (N일 전 대비 수익률)
        """
        # N일 전 가격 대비 현재 가격의 수익률
        momentum = df['종가'].pct_change(periods=self.lookback_period)
        return momentum
    
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
        df_copy = df.copy()
        
        # 모멘텀 계산
        df_copy['momentum'] = self.calculate_momentum(df_copy)
        
        # 신호 생성
        signals = pd.DataFrame(index=df_copy.index)
        signals['signal'] = 'HOLD'
        signals['position'] = 0
        signals['momentum'] = df_copy['momentum']
        
        # 매수 신호: 모멘텀이 buy_threshold 이상
        buy_condition = df_copy['momentum'] >= self.buy_threshold
        signals.loc[buy_condition, 'signal'] = 'BUY'
        signals.loc[buy_condition, 'position'] = 1
        
        # 매도 신호: 모멘텀이 sell_threshold 이하
        sell_condition = df_copy['momentum'] <= self.sell_threshold
        signals.loc[sell_condition, 'signal'] = 'SELL'
        signals.loc[sell_condition, 'position'] = -1
        
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
        signals = self.generate_signals(df)
        
        buy_signals = (signals['signal'] == 'BUY').sum()
        sell_signals = (signals['signal'] == 'SELL').sum()
        
        # 모멘텀 통계
        momentum = signals['momentum'].dropna()
        avg_momentum = momentum.mean()
        max_momentum = momentum.max()
        min_momentum = momentum.min()
        
        return {
            'strategy_name': self.name,
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'total_signals': buy_signals + sell_signals,
            'avg_momentum': avg_momentum,
            'max_momentum': max_momentum,
            'min_momentum': min_momentum,
            'buy_threshold': self.buy_threshold,
            'sell_threshold': self.sell_threshold,
        }


class DualMomentumStrategy(MomentumStrategy):
    """
    듀얼 모멘텀 전략
    
    절대 모멘텀만 사용 (0보다 크면 매수, 작으면 매도)
    """
    
    def __init__(self, lookback_period: int = 20):
        """
        Parameters
        ----------
        lookback_period : int
            모멘텀 계산 기간
        """
        super().__init__(
            lookback_period=lookback_period,
            buy_threshold=0.0,
            sell_threshold=0.0
        )
        self.name = f"듀얼 모멘텀 ({lookback_period}일)"
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        매매 신호 생성 (절대 모멘텀)
        
        Parameters
        ----------
        df : pd.DataFrame
            가격 데이터
        
        Returns
        -------
        pd.DataFrame
            매매 신호
        """
        df_copy = df.copy()
        
        # 모멘텀 계산
        df_copy['momentum'] = self.calculate_momentum(df_copy)
        
        # 신호 생성
        signals = pd.DataFrame(index=df_copy.index)
        signals['signal'] = 'HOLD'
        signals['position'] = 0
        signals['momentum'] = df_copy['momentum']
        
        # 모멘텀 변화 감지
        momentum_positive = df_copy['momentum'] > 0
        momentum_negative = df_copy['momentum'] <= 0
        
        # 이전 상태와 비교하여 신호 생성
        momentum_turned_positive = momentum_positive & (~momentum_positive.shift(1).fillna(False))
        momentum_turned_negative = momentum_negative & (~momentum_negative.shift(1).fillna(False))
        
        # 매수: 음수에서 양수로 전환
        signals.loc[momentum_turned_positive, 'signal'] = 'BUY'
        signals.loc[momentum_turned_positive, 'position'] = 1
        
        # 매도: 양수에서 음수로 전환
        signals.loc[momentum_turned_negative, 'signal'] = 'SELL'
        signals.loc[momentum_turned_negative, 'position'] = -1
        
        return signals

