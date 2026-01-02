"""
골든크로스 + RSI 필터 전략

골든크로스 신호에 RSI 필터를 추가하여 신호의 정확도를 높이는 전략
"""

import sys
from pathlib import Path
import pandas as pd
from typing import Dict, Optional

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from core.indicators import calculate_sma, calculate_rsi, detect_golden_cross, detect_dead_cross


class GoldenCrossRSIStrategy:
    """골든크로스 + RSI 필터 전략 클래스"""
    
    def __init__(
        self,
        fast_period: int = 20,
        slow_period: int = 50,
        rsi_period: int = 14,
        rsi_buy_threshold: float = 50.0,
        rsi_sell_threshold: float = 70.0,
        name: Optional[str] = None
    ):
        """
        Parameters
        ----------
        fast_period : int
            단기 이동평균 기간
        slow_period : int
            장기 이동평균 기간
        rsi_period : int
            RSI 계산 기간
        rsi_buy_threshold : float
            매수 시 RSI 최대값 (RSI가 이 값 이하일 때만 매수)
        rsi_sell_threshold : float
            매도 시 RSI 최소값 (RSI가 이 값 이상일 때만 매도)
        name : str, optional
            전략 이름
        """
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.rsi_period = rsi_period
        self.rsi_buy_threshold = rsi_buy_threshold
        self.rsi_sell_threshold = rsi_sell_threshold
        self.name = name or f"GoldenCross+RSI(SMA{fast_period}/{slow_period}, RSI{rsi_period})"
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        매매 신호 생성
        
        Parameters
        ----------
        df : pd.DataFrame
            가격 데이터 (종가 포함)
        
        Returns
        -------
        pd.DataFrame
            신호가 추가된 데이터프레임
            - signal: 1 (매수), 0 (매도/보유)
            - position: 1 (매수 시점), -1 (매도 시점), 0 (변화 없음)
        """
        df = df.copy()
        
        # SMA 계산
        df['SMA_fast'] = calculate_sma(df, window=self.fast_period)
        df['SMA_slow'] = calculate_sma(df, window=self.slow_period)
        
        # RSI 계산
        df['RSI'] = calculate_rsi(df, period=self.rsi_period)
        
        # 골든크로스/데드크로스 탐지
        df['golden_cross'] = detect_golden_cross(df, self.fast_period, self.slow_period)
        df['dead_cross'] = detect_dead_cross(df, self.fast_period, self.slow_period)
        
        # 기본 신호 (골든크로스/데드크로스)
        df['signal'] = 0
        df.loc[df['SMA_fast'] > df['SMA_slow'], 'signal'] = 1  # 매수
        df.loc[df['SMA_fast'] <= df['SMA_slow'], 'signal'] = 0  # 매도
        
        # RSI 필터 적용
        # 골든크로스 발생 + RSI가 임계값 이하일 때만 매수
        df.loc[
            (df['golden_cross']) & (df['RSI'] > self.rsi_buy_threshold),
            'signal'
        ] = 0  # RSI 필터로 매수 취소
        
        # 데드크로스 발생 + RSI가 임계값 이상일 때만 매도
        df.loc[
            (df['dead_cross']) & (df['RSI'] < self.rsi_sell_threshold),
            'signal'
        ] = 1  # RSI 필터로 매도 취소 (계속 보유)
        
        # 포지션 변화 (실제 거래 시점)
        df['position'] = df['signal'].diff()
        
        return df
    
    def analyze_current_status(self, df: pd.DataFrame) -> Dict:
        """
        현재 시장 상태 분석
        
        Parameters
        ----------
        df : pd.DataFrame
            신호가 포함된 데이터프레임
        
        Returns
        -------
        dict
            현재 상태 분석 결과
        """
        df = self.generate_signals(df)
        latest = df.iloc[-1]
        
        if pd.notna(latest['SMA_fast']) and pd.notna(latest['SMA_slow']) and pd.notna(latest['RSI']):
            gap = latest['SMA_fast'] - latest['SMA_slow']
            gap_percent = (gap / latest['SMA_slow']) * 100
            
            trend = "상승" if latest['SMA_fast'] > latest['SMA_slow'] else "하락"
            rsi_status = "과매수" if latest['RSI'] > 70 else "과매도" if latest['RSI'] < 30 else "보통"
            
            return {
                'date': df.index[-1],  # 날짜가 인덱스이므로 인덱스로 접근
                'price': latest['종가'],
                'sma_fast': latest['SMA_fast'],
                'sma_slow': latest['SMA_slow'],
                'rsi': latest['RSI'],
                'trend': trend,
                'gap_percent': gap_percent,
                'rsi_status': rsi_status,
                'golden_cross': latest['golden_cross'],
                'dead_cross': latest['dead_cross'],
                'signal': latest['signal'],
            }
        
        return {}
    
    def get_statistics(self, df: pd.DataFrame) -> Dict:
        """
        전략 통계 계산
        
        Parameters
        ----------
        df : pd.DataFrame
            가격 데이터
        
        Returns
        -------
        dict
            통계 정보
        """
        df = self.generate_signals(df)
        
        gc_count = df['golden_cross'].sum()
        dc_count = df['dead_cross'].sum()
        total_crosses = gc_count + dc_count
        
        # RSI 필터로 인한 거래 취소 횟수
        filtered_buys = ((df['golden_cross']) & (df['RSI'] > self.rsi_buy_threshold)).sum()
        filtered_sells = ((df['dead_cross']) & (df['RSI'] < self.rsi_sell_threshold)).sum()
        
        return {
            'strategy_name': self.name,
            'fast_period': self.fast_period,
            'slow_period': self.slow_period,
            'rsi_period': self.rsi_period,
            'golden_cross_count': int(gc_count),
            'dead_cross_count': int(dc_count),
            'total_crosses': int(total_crosses),
            'filtered_buys': int(filtered_buys),
            'filtered_sells': int(filtered_sells),
        }
    
    def __repr__(self):
        return f"GoldenCrossRSIStrategy({self.name})"

