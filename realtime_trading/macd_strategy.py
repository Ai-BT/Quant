"""
MACD + Trend Filter 전략 (실시간 거래용)

MACD 크로스오버 신호에 Trend Filter를 추가하여 신호의 정확도를 높이는 전략
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional


def calculate_ema(df: pd.DataFrame, column: str = '종가', span: int = 20) -> pd.Series:
    """지수 이동평균선 (EMA) 계산"""
    return df[column].ewm(span=span, adjust=False).mean()


def calculate_sma(df: pd.DataFrame, column: str = '종가', window: int = 20) -> pd.Series:
    """단순 이동평균선 (SMA) 계산"""
    return df[column].rolling(window=window).mean()


class MACDRealtimeStrategy:
    """MACD + Trend Filter 전략 클래스 (실시간 거래용)"""

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
        volume_multiplier: float = 1.2
    ):
        """
        Parameters
        ----------
        macd_fast : int
            MACD 단기 EMA 기간
        macd_slow : int
            MACD 장기 EMA 기간
        macd_signal : int
            Signal Line EMA 기간
        trend_ma_period : int
            추세 확인용 이동평균 기간
        trend_ma_type : str
            추세 MA 타입 ('SMA' or 'EMA')
        use_trend_filter : bool
            Trend Filter 사용 여부
        use_histogram_filter : bool
            Histogram 필터 사용 여부
        min_histogram : float
            최소 Histogram 값
        use_dual_trend : bool
            이중 트렌드 필터 사용 여부
        mid_trend_period : int
            중기 트렌드 MA 기간
        use_volume_filter : bool
            거래량 필터 사용 여부
        volume_ma_period : int
            거래량 MA 기간
        volume_multiplier : float
            평균 거래량 대비 배수
        """
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

        self.name = f"MACD({macd_fast}/{macd_slow}/{macd_signal})+TrendFilter({trend_ma_period})"

    def analyze(self, df: pd.DataFrame) -> Dict:
        """
        현재 시장 상태 분석 및 매매 신호 생성

        Parameters
        ----------
        df : pd.DataFrame
            가격 데이터 (최소 trend_ma_period 이상의 데이터 필요)

        Returns
        -------
        dict
            분석 결과 및 매매 신호
        """
        if len(df) < self.trend_ma_period:
            return {
                'signal': 'HOLD',
                'reason': '데이터 부족',
                'can_trade': False
            }

        df = df.copy()

        # MACD 계산
        ema_fast = calculate_ema(df, span=self.macd_fast)
        ema_slow = calculate_ema(df, span=self.macd_slow)

        df['MACD'] = ema_fast - ema_slow
        df['MACD_Signal'] = df['MACD'].ewm(span=self.macd_signal, adjust=False).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']

        # Trend MA 계산
        if self.use_trend_filter:
            if self.trend_ma_type == 'SMA':
                df['Trend_MA'] = calculate_sma(df, window=self.trend_ma_period)
            else:
                df['Trend_MA'] = calculate_ema(df, span=self.trend_ma_period)

            # 이중 트렌드 필터
            if self.use_dual_trend:
                if self.trend_ma_type == 'SMA':
                    df['Mid_Trend_MA'] = calculate_sma(df, window=self.mid_trend_period)
                else:
                    df['Mid_Trend_MA'] = calculate_ema(df, span=self.mid_trend_period)

        # Volume MA 계산
        if self.use_volume_filter and '거래량' in df.columns:
            df['Volume_MA'] = df['거래량'].rolling(window=self.volume_ma_period).mean()

        # 최신 데이터
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest

        # 데이터 유효성 체크
        if pd.isna(latest['MACD']) or pd.isna(latest['MACD_Signal']):
            return {
                'signal': 'HOLD',
                'reason': '지표 계산 불가',
                'can_trade': False
            }

        # 매매 신호 생성
        signal, reason = self._generate_signal(df, latest, prev)

        # 시장 상태 분석
        macd_value = latest['MACD']
        signal_value = latest['MACD_Signal']
        histogram = latest['MACD_Histogram']

        trend = "상승" if macd_value > signal_value else "하락"

        result = {
            'signal': signal,
            'reason': reason,
            'can_trade': True,
            'price': latest['종가'],
            'macd': macd_value,
            'macd_signal': signal_value,
            'histogram': histogram,
            'trend': trend
        }

        # Trend Filter 정보 추가
        if self.use_trend_filter:
            result['trend_ma'] = latest['Trend_MA']
            result['price_vs_trend'] = "상승" if latest['종가'] > latest['Trend_MA'] else "하락"

            if self.use_dual_trend:
                result['mid_trend_ma'] = latest['Mid_Trend_MA']

        return result

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
        # MACD 크로스오버 감지
        macd_cross_up = (prev['MACD'] <= prev['MACD_Signal']) and (latest['MACD'] > latest['MACD_Signal'])
        macd_cross_down = (prev['MACD'] >= prev['MACD_Signal']) and (latest['MACD'] < latest['MACD_Signal'])

        # 매수 신호 체크
        if macd_cross_up:
            # Trend Filter 체크
            if self.use_trend_filter:
                if latest['종가'] <= latest['Trend_MA']:
                    return 'HOLD', f'MACD 골든크로스 발생했으나 추세선 아래 (가격: {latest["종가"]:,.0f}, 추세선: {latest["Trend_MA"]:,.0f})'

                # 이중 트렌드 필터
                if self.use_dual_trend:
                    if latest['종가'] <= latest['Mid_Trend_MA'] or latest['Mid_Trend_MA'] <= latest['Trend_MA']:
                        return 'HOLD', 'MACD 골든크로스 발생했으나 이중 트렌드 조건 미충족'

            # Histogram 필터 체크
            if self.use_histogram_filter:
                if latest['MACD_Histogram'] <= self.min_histogram:
                    return 'HOLD', f'MACD 골든크로스 발생했으나 Histogram 부족 ({latest["MACD_Histogram"]:.2f})'

            # Volume 필터 체크
            if self.use_volume_filter and '거래량' in df.columns:
                if latest['거래량'] <= latest['Volume_MA'] * self.volume_multiplier:
                    return 'HOLD', 'MACD 골든크로스 발생했으나 거래량 부족'

            return 'BUY', f'MACD 골든크로스 발생 (MACD: {latest["MACD"]:.2f}, Signal: {latest["MACD_Signal"]:.2f})'

        # 매도 신호 체크
        if macd_cross_down:
            return 'SELL', f'MACD 데드크로스 발생 (MACD: {latest["MACD"]:.2f}, Signal: {latest["MACD_Signal"]:.2f})'

        # Trend Filter로 추가 매도 조건
        if self.use_trend_filter:
            if latest['종가'] < latest['Trend_MA']:
                return 'SELL', f'추세선 하향 돌파 (가격: {latest["종가"]:,.0f}, 추세선: {latest["Trend_MA"]:,.0f})'

        # 신호 없음
        if latest['MACD'] > latest['MACD_Signal']:
            return 'HOLD', f'상승 추세 유지 (Histogram: {latest["MACD_Histogram"]:.2f})'
        else:
            return 'HOLD', f'하락 추세 유지 (Histogram: {latest["MACD_Histogram"]:.2f})'

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
            'macd_fast': self.macd_fast,
            'macd_slow': self.macd_slow,
            'macd_signal': self.macd_signal,
            'trend_ma_period': self.trend_ma_period,
            'trend_ma_type': self.trend_ma_type,
            'use_trend_filter': self.use_trend_filter,
            'use_histogram_filter': self.use_histogram_filter,
            'use_dual_trend': self.use_dual_trend,
            'use_volume_filter': self.use_volume_filter
        }
