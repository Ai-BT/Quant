"""
기술적 지표 계산 함수

공통으로 사용되는 지표 계산 함수들
"""

import pandas as pd
import numpy as np


def calculate_sma(df: pd.DataFrame, column: str = '종가', window: int = 20) -> pd.Series:
    """
    단순 이동평균선 (SMA) 계산
    
    Parameters
    ----------
    df : pd.DataFrame
        가격 데이터
    column : str
        계산할 컬럼명
    window : int
        이동평균 기간
    
    Returns
    -------
    pd.Series
        SMA 값
    """
    return df[column].rolling(window=window).mean()


def calculate_ema(df: pd.DataFrame, column: str = '종가', span: int = 20) -> pd.Series:
    """
    지수 이동평균선 (EMA) 계산
    
    Parameters
    ----------
    df : pd.DataFrame
        가격 데이터
    column : str
        계산할 컬럼명
    span : int
        EMA 기간
    
    Returns
    -------
    pd.Series
        EMA 값
    """
    return df[column].ewm(span=span, adjust=False).mean()


def calculate_rsi(df: pd.DataFrame, column: str = '종가', period: int = 14) -> pd.Series:
    """
    RSI (Relative Strength Index) 계산
    
    Parameters
    ----------
    df : pd.DataFrame
        가격 데이터
    column : str
        계산할 컬럼명
    period : int
        RSI 기간 (기본 14)
    
    Returns
    -------
    pd.Series
        RSI 값 (0~100)
    """
    delta = df[column].diff()
    
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def detect_golden_cross(
    df: pd.DataFrame,
    fast_period: int = 20,
    slow_period: int = 50
) -> pd.Series:
    """
    골든크로스 탐지
    
    Parameters
    ----------
    df : pd.DataFrame
        가격 데이터 (종가 컬럼 필요)
    fast_period : int
        단기 이동평균 기간
    slow_period : int
        장기 이동평균 기간
    
    Returns
    -------
    pd.Series
        골든크로스 발생 여부 (Boolean)
    """
    sma_fast = calculate_sma(df, window=fast_period)
    sma_slow = calculate_sma(df, window=slow_period)
    
    golden_cross = (
        (sma_fast.shift(1) < sma_slow.shift(1)) & 
        (sma_fast > sma_slow)
    )
    
    return golden_cross


def detect_dead_cross(
    df: pd.DataFrame,
    fast_period: int = 20,
    slow_period: int = 50
) -> pd.Series:
    """
    데드크로스 탐지
    
    Parameters
    ----------
    df : pd.DataFrame
        가격 데이터 (종가 컬럼 필요)
    fast_period : int
        단기 이동평균 기간
    slow_period : int
        장기 이동평균 기간
    
    Returns
    -------
    pd.Series
        데드크로스 발생 여부 (Boolean)
    """
    sma_fast = calculate_sma(df, window=fast_period)
    sma_slow = calculate_sma(df, window=slow_period)
    
    dead_cross = (
        (sma_fast.shift(1) > sma_slow.shift(1)) & 
        (sma_fast < sma_slow)
    )
    
    return dead_cross

