"""
MACD + Trend Filter 전략 구현

MACD (Moving Average Convergence Divergence):
- 단기 EMA와 장기 EMA의 차이로 추세 강도 측정
- Signal Line과의 교차로 매매 신호 생성

Trend Filter:
- 200일 SMA로 큰 추세 방향 확인
- 상승 추세에서만 매수, 하락 추세 감지 시 매도
"""

import pandas as pd
import numpy as np
from typing import Optional


class MACDTrendStrategy:
    """
    MACD + Trend Filter 전략
    
    Parameters
    ----------
    macd_fast : int
        MACD 단기 EMA 기간 (기본값: 12)
    macd_slow : int
        MACD 장기 EMA 기간 (기본값: 26)
    macd_signal : int
        Signal Line EMA 기간 (기본값: 9)
    trend_ma_period : int
        Trend Filter 이동평균 기간 (기본값: 200)
    trend_ma_type : str
        Trend Filter MA 종류 ('SMA' or 'EMA')
    use_trend_filter : bool
        Trend Filter 사용 여부
    use_histogram_filter : bool
        Histogram 필터 사용 여부
    min_histogram : float
        최소 Histogram 값
    use_dual_trend : bool
        이중 트렌드 필터 사용 여부
    mid_trend_period : int
        중기 트렌드 MA 기간 (기본값: 50)
    use_volume_filter : bool
        거래량 필터 사용 여부
    volume_ma_period : int
        거래량 MA 기간
    volume_multiplier : float
        평균 거래량 대비 배수
    """
    
    def __init__(
        self,
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9,
        trend_ma_period: int = 200,
        trend_ma_type: str = 'SMA',
        use_trend_filter: bool = True,
        use_histogram_filter: bool = True,
        min_histogram: float = 0,
        use_dual_trend: bool = False,
        mid_trend_period: int = 50,
        use_volume_filter: bool = False,
        volume_ma_period: int = 20,
        volume_multiplier: float = 1.2,
    ):
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.trend_ma_period = trend_ma_period
        self.trend_ma_type = trend_ma_type
        self.use_trend_filter = use_trend_filter
        self.use_histogram_filter = use_histogram_filter
        self.min_histogram = min_histogram
        self.use_dual_trend = use_dual_trend
        self.mid_trend_period = mid_trend_period
        self.use_volume_filter = use_volume_filter
        self.volume_ma_period = volume_ma_period
        self.volume_multiplier = volume_multiplier
    
    def calculate_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        MACD, Signal, Histogram 계산
        
        Parameters
        ----------
        df : pd.DataFrame
            가격 데이터 (종가 컬럼 필요)
        
        Returns
        -------
        pd.DataFrame
            MACD 지표가 추가된 데이터프레임
        """
        df_copy = df.copy()
        
        # EMA 계산
        ema_fast = df_copy['종가'].ewm(span=self.macd_fast, adjust=False).mean()
        ema_slow = df_copy['종가'].ewm(span=self.macd_slow, adjust=False).mean()
        
        # MACD Line = Fast EMA - Slow EMA
        df_copy['MACD'] = ema_fast - ema_slow
        
        # Signal Line = MACD의 EMA
        df_copy['MACD_Signal'] = df_copy['MACD'].ewm(span=self.macd_signal, adjust=False).mean()
        
        # Histogram = MACD - Signal
        df_copy['MACD_Histogram'] = df_copy['MACD'] - df_copy['MACD_Signal']
        
        return df_copy
    
    def calculate_trend_ma(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Trend Filter용 이동평균 계산
        
        Parameters
        ----------
        df : pd.DataFrame
            가격 데이터
        
        Returns
        -------
        pd.DataFrame
            Trend MA가 추가된 데이터프레임
        """
        df_copy = df.copy()
        
        if self.trend_ma_type == 'SMA':
            df_copy['Trend_MA'] = df_copy['종가'].rolling(window=self.trend_ma_period).mean()
        else:  # EMA
            df_copy['Trend_MA'] = df_copy['종가'].ewm(span=self.trend_ma_period, adjust=False).mean()
        
        # 이중 트렌드 필터
        if self.use_dual_trend:
            if self.trend_ma_type == 'SMA':
                df_copy['Mid_Trend_MA'] = df_copy['종가'].rolling(window=self.mid_trend_period).mean()
            else:
                df_copy['Mid_Trend_MA'] = df_copy['종가'].ewm(span=self.mid_trend_period, adjust=False).mean()
        
        return df_copy
    
    def calculate_volume_ma(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        거래량 이동평균 계산
        
        Parameters
        ----------
        df : pd.DataFrame
            거래량 데이터
        
        Returns
        -------
        pd.DataFrame
            거래량 MA가 추가된 데이터프레임
        """
        df_copy = df.copy()
        
        if '거래량' in df_copy.columns:
            df_copy['Volume_MA'] = df_copy['거래량'].rolling(window=self.volume_ma_period).mean()
        
        return df_copy
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        매매 신호 생성
        
        Parameters
        ----------
        df : pd.DataFrame
            가격 데이터
        
        Returns
        -------
        pd.DataFrame
            매매 신호가 포함된 데이터프레임
        """
        # MACD 계산
        df_with_macd = self.calculate_macd(df)
        
        # Trend Filter 계산
        if self.use_trend_filter:
            df_with_macd = self.calculate_trend_ma(df_with_macd)
        
        # Volume Filter 계산
        if self.use_volume_filter:
            df_with_macd = self.calculate_volume_ma(df_with_macd)
        
        # 신호 초기화
        signals_df = pd.DataFrame(index=df_with_macd.index)
        signals_df['signal'] = 'HOLD'
        
        # MACD 크로스오버 감지
        macd_cross_up = (
            (df_with_macd['MACD'] > df_with_macd['MACD_Signal']) &
            (df_with_macd['MACD'].shift(1) <= df_with_macd['MACD_Signal'].shift(1))
        )
        
        macd_cross_down = (
            (df_with_macd['MACD'] < df_with_macd['MACD_Signal']) &
            (df_with_macd['MACD'].shift(1) >= df_with_macd['MACD_Signal'].shift(1))
        )
        
        # 매수 조건
        buy_condition = macd_cross_up
        
        # Trend Filter 적용
        if self.use_trend_filter:
            trend_up = df_with_macd['종가'] > df_with_macd['Trend_MA']
            buy_condition = buy_condition & trend_up
            
            # 이중 트렌드 필터
            if self.use_dual_trend:
                mid_trend_up = df_with_macd['종가'] > df_with_macd['Mid_Trend_MA']
                ma_aligned = df_with_macd['Mid_Trend_MA'] > df_with_macd['Trend_MA']
                buy_condition = buy_condition & mid_trend_up & ma_aligned
        
        # Histogram 필터 적용
        if self.use_histogram_filter:
            histogram_positive = df_with_macd['MACD_Histogram'] > self.min_histogram
            buy_condition = buy_condition & histogram_positive
        
        # Volume 필터 적용
        if self.use_volume_filter and '거래량' in df_with_macd.columns:
            volume_high = df_with_macd['거래량'] > (df_with_macd['Volume_MA'] * self.volume_multiplier)
            buy_condition = buy_condition & volume_high
        
        # 매도 조건
        sell_condition = macd_cross_down
        
        # Trend Filter로 추가 매도 조건
        if self.use_trend_filter:
            trend_down = df_with_macd['종가'] < df_with_macd['Trend_MA']
            sell_condition = sell_condition | trend_down
        
        # 신호 적용
        signals_df.loc[buy_condition, 'signal'] = 'BUY'
        signals_df.loc[sell_condition, 'signal'] = 'SELL'
        
        # Position 계산 (backtest_engine 호환)
        signals_df['position'] = signals_df['signal'].apply(
            lambda x: 1 if x == 'BUY' else (-1 if x == 'SELL' else 0)
        ).diff().fillna(0)
        
        # 지표 데이터 병합
        signals_df = pd.concat([signals_df, df_with_macd[['MACD', 'MACD_Signal', 'MACD_Histogram']]], axis=1)
        if self.use_trend_filter:
            signals_df['Trend_MA'] = df_with_macd['Trend_MA']
            if self.use_dual_trend:
                signals_df['Mid_Trend_MA'] = df_with_macd['Mid_Trend_MA']
        
        return signals_df
    
    def get_statistics(self, df: pd.DataFrame, signals: pd.DataFrame) -> dict:
        """
        전략 통계 계산
        
        Parameters
        ----------
        df : pd.DataFrame
            가격 데이터
        signals : pd.DataFrame
            매매 신호
        
        Returns
        -------
        dict
            전략 통계
        """
        buy_signals = (signals['signal'] == 'BUY').sum()
        sell_signals = (signals['signal'] == 'SELL').sum()
        
        stats = {
            'total_signals': buy_signals + sell_signals,
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'macd_fast': self.macd_fast,
            'macd_slow': self.macd_slow,
            'macd_signal': self.macd_signal,
            'trend_ma_period': self.trend_ma_period if self.use_trend_filter else None,
            'use_trend_filter': self.use_trend_filter,
            'use_histogram_filter': self.use_histogram_filter,
            'use_dual_trend': self.use_dual_trend,
            'use_volume_filter': self.use_volume_filter,
        }
        
        return stats




