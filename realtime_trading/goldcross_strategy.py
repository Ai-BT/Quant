"""
골든크로스 + RSI 필터 전략 (실시간 거래용)

골든크로스 신호에 RSI 필터를 추가하여 신호의 정확도를 높이는 전략
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional


def calculate_sma(df: pd.DataFrame, column: str = '종가', window: int = 20) -> pd.Series:
    """단순 이동평균선 (SMA) 계산"""
    return df[column].rolling(window=window).mean()


def calculate_rsi(df: pd.DataFrame, column: str = '종가', period: int = 14) -> pd.Series:
    """RSI (Relative Strength Index) 계산"""
    delta = df[column].diff()

    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def detect_golden_cross(df: pd.DataFrame, fast_period: int = 20, slow_period: int = 50) -> pd.Series:
    """골든크로스 탐지"""
    sma_fast = calculate_sma(df, window=fast_period)
    sma_slow = calculate_sma(df, window=slow_period)

    golden_cross = (
        (sma_fast.shift(1) < sma_slow.shift(1)) &
        (sma_fast > sma_slow)
    )

    return golden_cross


def detect_dead_cross(df: pd.DataFrame, fast_period: int = 20, slow_period: int = 50) -> pd.Series:
    """데드크로스 탐지"""
    sma_fast = calculate_sma(df, window=fast_period)
    sma_slow = calculate_sma(df, window=slow_period)

    dead_cross = (
        (sma_fast.shift(1) > sma_slow.shift(1)) &
        (sma_fast < sma_slow)
    )

    return dead_cross


class GoldenCrossStrategy:
    """골든크로스 + RSI 필터 전략 클래스 (실시간 거래용)"""

    def __init__(
        self,
        fast_period: int = 20,
        slow_period: int = 50,
        rsi_period: int = 14,
        rsi_buy_threshold: float = 50.0,
        rsi_sell_threshold: float = 70.0
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
        """
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.rsi_period = rsi_period
        self.rsi_buy_threshold = rsi_buy_threshold
        self.rsi_sell_threshold = rsi_sell_threshold
        self.name = f"GoldenCross+RSI(SMA{fast_period}/{slow_period}, RSI{rsi_period})"

    def analyze(self, df: pd.DataFrame) -> Dict:
        """
        현재 시장 상태 분석 및 매매 신호 생성

        Parameters
        ----------
        df : pd.DataFrame
            가격 데이터 (최소 slow_period 이상의 데이터 필요)

        Returns
        -------
        dict
            분석 결과 및 매매 신호
        """
        if len(df) < self.slow_period:
            return {
                'signal': 'HOLD',
                'reason': '데이터 부족',
                'can_trade': False
            }

        df = df.copy()

        # SMA 계산
        df['SMA_fast'] = calculate_sma(df, window=self.fast_period)
        df['SMA_slow'] = calculate_sma(df, window=self.slow_period)

        # RSI 계산
        df['RSI'] = calculate_rsi(df, period=self.rsi_period)

        # 골든크로스/데드크로스 탐지
        df['golden_cross'] = detect_golden_cross(df, self.fast_period, self.slow_period)
        df['dead_cross'] = detect_dead_cross(df, self.fast_period, self.slow_period)

        # 최신 데이터
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest

        # 데이터 유효성 체크
        if pd.isna(latest['SMA_fast']) or pd.isna(latest['SMA_slow']) or pd.isna(latest['RSI']):
            return {
                'signal': 'HOLD',
                'reason': '지표 계산 불가',
                'can_trade': False
            }

        # 매매 신호 생성
        signal, reason = self._generate_signal(df, latest, prev)

        # 시장 상태 분석
        gap = latest['SMA_fast'] - latest['SMA_slow']
        gap_percent = (gap / latest['SMA_slow']) * 100
        trend = "상승" if latest['SMA_fast'] > latest['SMA_slow'] else "하락"
        rsi_status = "과매수" if latest['RSI'] > 70 else "과매도" if latest['RSI'] < 30 else "보통"

        return {
            'signal': signal,
            'reason': reason,
            'can_trade': True,
            'price': latest['종가'],
            'sma_fast': latest['SMA_fast'],
            'sma_slow': latest['SMA_slow'],
            'rsi': latest['RSI'],
            'trend': trend,
            'gap_percent': gap_percent,
            'rsi_status': rsi_status,
            'golden_cross': latest['golden_cross'],
            'dead_cross': latest['dead_cross']
        }

    def _generate_signal(
        self,
        df: pd.DataFrame,
        latest: pd.Series,
        prev: pd.Series
    ) -> Tuple[str, str]:
        """
        매매 신호 생성

        Parameters
        ----------
        df : pd.DataFrame
            전체 데이터
        latest : pd.Series
            최신 데이터
        prev : pd.Series
            이전 데이터

        Returns
        -------
        tuple
            (신호, 사유)
        """
        # 골든크로스 발생 + RSI 필터
        if latest['golden_cross']:
            if latest['RSI'] <= self.rsi_buy_threshold:
                return 'BUY', f'골든크로스 발생 (RSI: {latest["RSI"]:.1f})'
            else:
                return 'HOLD', f'골든크로스 발생했으나 RSI 과매수 (RSI: {latest["RSI"]:.1f})'

        # 데드크로스 발생 + RSI 필터
        if latest['dead_cross']:
            if latest['RSI'] >= self.rsi_sell_threshold:
                return 'SELL', f'데드크로스 발생 (RSI: {latest["RSI"]:.1f})'
            else:
                return 'HOLD', f'데드크로스 발생했으나 RSI 낮음 (RSI: {latest["RSI"]:.1f})'

        # 크로스 없음 - 현재 추세 유지
        if latest['SMA_fast'] > latest['SMA_slow']:
            return 'HOLD', f'상승 추세 유지 (갭: {((latest["SMA_fast"] - latest["SMA_slow"]) / latest["SMA_slow"] * 100):.2f}%)'
        else:
            return 'HOLD', f'하락 추세 유지 (갭: {((latest["SMA_fast"] - latest["SMA_slow"]) / latest["SMA_slow"] * 100):.2f}%)'

    def get_strategy_info(self) -> Dict:
        """
        전략 정보 반환

        Returns
        -------
        dict
            전략 설정 정보
        """
        return {
            'name': self.name,
            'fast_period': self.fast_period,
            'slow_period': self.slow_period,
            'rsi_period': self.rsi_period,
            'rsi_buy_threshold': self.rsi_buy_threshold,
            'rsi_sell_threshold': self.rsi_sell_threshold
        }
