"""
실시간 데이터 수집 모듈

Upbit API를 통한 실시간 가격 데이터 수집
"""

import pandas as pd
import requests
import time
from datetime import datetime
from typing import Optional


class RealtimeDataFetcher:
    """실시간 데이터 수집 클래스"""

    def __init__(self, market: str, candle_minutes: int = 1):
        """
        Parameters
        ----------
        market : str
            마켓 코드 (예: 'KRW-BTC')
        candle_minutes : int
            분봉 단위 (1, 3, 5, 10, 15, 30, 60, 240)
        """
        self.market = market
        self.candle_minutes = candle_minutes
        self.base_url = f"https://api.upbit.com/v1/candles/minutes/{candle_minutes}"
        self.headers = {"accept": "application/json"}

    def fetch_latest_candles(self, count: int = 200) -> Optional[pd.DataFrame]:
        """
        최근 캔들 데이터 수집

        Parameters
        ----------
        count : int
            수집할 캔들 개수 (최대 200)

        Returns
        -------
        pd.DataFrame or None
            가격 데이터 (실패 시 None)
        """
        try:
            params = {
                'market': self.market,
                'count': min(count, 200)
            }

            response = requests.get(self.base_url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            if not data:
                return None

            df = pd.DataFrame(data)
            df['날짜'] = pd.to_datetime(df['candle_date_time_kst'])
            df = df.sort_values('날짜')
            df['종가'] = df['trade_price']
            df['시가'] = df['opening_price']
            df['고가'] = df['high_price']
            df['저가'] = df['low_price']
            df['거래량'] = df['candle_acc_trade_volume']

            return df

        except Exception as e:
            print(f"⚠️  데이터 수집 중 오류 발생: {e}")
            return None

    def get_current_price(self) -> Optional[float]:
        """
        현재가 조회

        Returns
        -------
        float or None
            현재가 (실패 시 None)
        """
        try:
            url = "https://api.upbit.com/v1/ticker"
            params = {'markets': self.market}

            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            if data and len(data) > 0:
                return data[0]['trade_price']

            return None

        except Exception as e:
            print(f"⚠️  현재가 조회 중 오류 발생: {e}")
            return None

    def get_market_info(self) -> dict:
        """
        마켓 정보 조회

        Returns
        -------
        dict
            마켓 정보
        """
        try:
            url = "https://api.upbit.com/v1/ticker"
            params = {'markets': self.market}

            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            if data and len(data) > 0:
                ticker = data[0]
                return {
                    'market': self.market,
                    'current_price': ticker['trade_price'],
                    'opening_price': ticker['opening_price'],
                    'high_price': ticker['high_price'],
                    'low_price': ticker['low_price'],
                    'prev_closing_price': ticker['prev_closing_price'],
                    'change_rate': ticker['signed_change_rate'] * 100,
                    'acc_trade_volume_24h': ticker['acc_trade_volume_24h'],
                    'timestamp': datetime.now()
                }

            return {}

        except Exception as e:
            print(f"⚠️  마켓 정보 조회 중 오류 발생: {e}")
            return {}
