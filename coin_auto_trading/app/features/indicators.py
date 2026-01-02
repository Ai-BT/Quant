"""
기술적 지표 계산 (SMA, MACD, RSI 등)
"""
from typing import List
import numpy as np
from app.data.candle import Candle


def sma(prices: List[float], period: int) -> List[float]:
    """
    Simple Moving Average
    
    Parameters
    ----------
    prices : List[float]
        가격 리스트
    period : int
        기간
    
    Returns
    -------
    List[float]
        SMA 값 리스트 (앞부분은 None으로 채워짐)
    """
    result = [None] * (period - 1)
    
    for i in range(period - 1, len(prices)):
        window = prices[i - period + 1:i + 1]
        avg = sum(window) / period
        result.append(avg)
    
    return result


def ema(prices: List[float], period: int) -> List[float]:
    """
    Exponential Moving Average
    
    Parameters
    ----------
    prices : List[float]
        가격 리스트
    period : int
        기간
    
    Returns
    -------
    List[float]
        EMA 값 리스트
    """
    if not prices:
        return []
    
    multiplier = 2 / (period + 1)
    result = [prices[0]]  # 첫 값은 그대로
    
    for price in prices[1:]:
        ema_value = (price - result[-1]) * multiplier + result[-1]
        result.append(ema_value)
    
    return result


def macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> dict:
    """
    MACD (Moving Average Convergence Divergence)
    
    Parameters
    ----------
    prices : List[float]
        가격 리스트
    fast : int
        빠른 EMA 기간
    slow : int
        느린 EMA 기간
    signal : int
        시그널 라인 기간
    
    Returns
    -------
    dict
        {'macd': List[float], 'signal': List[float], 'histogram': List[float]}
    """
    ema_fast = ema(prices, fast)
    ema_slow = ema(prices, slow)
    
    # MACD 라인
    macd_line = [f - s if f is not None and s is not None else None 
                 for f, s in zip(ema_fast, ema_slow)]
    
    # 시그널 라인 (MACD의 EMA)
    macd_values = [m for m in macd_line if m is not None]
    if not macd_values:
        return {'macd': macd_line, 'signal': [], 'histogram': []}
    
    signal_line_raw = ema(macd_values, signal)
    
    # None 값 채우기
    signal_line = [None] * (len(macd_line) - len(signal_line_raw))
    signal_line.extend(signal_line_raw)
    
    # 히스토그램
    histogram = [m - s if m is not None and s is not None else None
                 for m, s in zip(macd_line, signal_line)]
    
    return {
        'macd': macd_line,
        'signal': signal_line,
        'histogram': histogram
    }


def rsi(prices: List[float], period: int = 14) -> List[float]:
    """
    Relative Strength Index
    
    Parameters
    ----------
    prices : List[float]
        가격 리스트
    period : int
        기간
    
    Returns
    -------
    List[float]
        RSI 값 리스트 (0-100)
    """
    if len(prices) < period + 1:
        return [None] * len(prices)
    
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    
    result = [None] * period
    
    # 초기 평균
    gains = [d if d > 0 else 0 for d in deltas[:period]]
    losses = [-d if d < 0 else 0 for d in deltas[:period]]
    
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    
    if avg_loss == 0:
        rsi_value = 100
    else:
        rs = avg_gain / avg_loss
        rsi_value = 100 - (100 / (1 + rs))
    
    result.append(rsi_value)
    
    # 이후 값들 계산 (지수 이동 평균 사용)
    for i in range(period, len(deltas)):
        gain = deltas[i] if deltas[i] > 0 else 0
        loss = -deltas[i] if deltas[i] < 0 else 0
        
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        
        if avg_loss == 0:
            rsi_value = 100
        else:
            rs = avg_gain / avg_loss
            rsi_value = 100 - (100 / (1 + rs))
        
        result.append(rsi_value)
    
    return result


def calculate_features(candles: List[Candle]) -> dict:
    """
    캔들 데이터에서 피처 계산
    
    Parameters
    ----------
    candles : List[Candle]
        캔들 리스트
    
    Returns
    -------
    dict
        계산된 피처들
    """
    if not candles:
        return {}
    
    closes = [c.close for c in candles]
    
    features = {
        'sma_5': sma(closes, 5),
        'sma_20': sma(closes, 20),
        'sma_50': sma(closes, 50),
        'ema_12': ema(closes, 12),
        'ema_26': ema(closes, 26),
        'rsi': rsi(closes, 14),
        'macd': macd(closes),
        'current_price': closes[-1] if closes else None
    }
    
    return features

