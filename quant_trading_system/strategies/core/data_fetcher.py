"""
데이터 수집 모듈

Upbit API를 통한 가격 데이터 수집
"""

import pandas as pd
import requests
import time
from datetime import datetime


def fetch_daily_data(market: str, days: int):
    """
    Upbit API에서 일봉 데이터 수집
    
    Parameters
    ----------
    market : str
        마켓 코드 (예: 'KRW-BTC')
    days : int
        수집할 일수
    
    Returns
    -------
    pd.DataFrame
        가격 데이터
    """
    url = "https://api.upbit.com/v1/candles/days"
    headers = {"accept": "application/json"}
    
    all_data = []
    last_timestamp = None
    
    print(f"📡 {market} 데이터 수집 중...")
    
    while len(all_data) < days:
        params = {
            'market': market,
            'count': min(200, days - len(all_data)),
        }
        
        if last_timestamp:
            params['to'] = last_timestamp
        
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        
        if not data:
            break
        
        all_data.extend(data)
        last_timestamp = data[-1]['candle_date_time_utc']
        
        print(f"   수집 완료: {len(all_data)}/{days}일")
        time.sleep(0.1)  # API 요청 제한 방지
    
    print(f"✅ 총 {len(all_data)}일 데이터 수집 완료!\n")
    
    df = pd.DataFrame(all_data)
    df['날짜'] = pd.to_datetime(df['candle_date_time_kst'])
    df = df.sort_values('날짜')
    df['종가'] = df['trade_price']
    df['시가'] = df['opening_price']
    df['고가'] = df['high_price']
    df['저가'] = df['low_price']
    df['거래량'] = df['candle_acc_trade_volume']
    
    # 날짜를 인덱스로 설정
    df = df.set_index('날짜')
    
    return df


def fetch_minute_data(market: str, minutes: int = 1, count: int = 1000):
    """
    Upbit API에서 분봉 데이터 수집
    
    Parameters
    ----------
    market : str
        마켓 코드
    minutes : int
        분봉 단위 (1, 3, 5, 10, 15, 30, 60, 240)
    count : int
        수집할 캔들 개수
    
    Returns
    -------
    pd.DataFrame
        가격 데이터
    """
    url = f"https://api.upbit.com/v1/candles/minutes/{minutes}"
    headers = {"accept": "application/json"}
    
    all_data = []
    last_timestamp = None
    
    print(f"📡 {market} {minutes}분봉 데이터 수집 중...")
    
    while len(all_data) < count:
        params = {
            'market': market,
            'count': min(200, count - len(all_data)),
        }
        
        if last_timestamp:
            params['to'] = last_timestamp
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                break
            
            all_data.extend(data)
            last_timestamp = data[-1]['candle_date_time_utc']
            
            print(f"   수집 완료: {len(all_data)}/{count}개")
            time.sleep(0.1)  # API 요청 제한 방지
            
        except Exception as e:
            print(f"⚠️  데이터 수집 중 오류 발생: {e}")
            break
    
    print(f"✅ 총 {len(all_data)}개 캔들 수집 완료!\n")
    
    df = pd.DataFrame(all_data)
    df['날짜'] = pd.to_datetime(df['candle_date_time_kst'])
    df = df.sort_values('날짜')
    df['종가'] = df['trade_price']
    df['시가'] = df['opening_price']
    df['고가'] = df['high_price']
    df['저가'] = df['low_price']
    df['거래량'] = df['candle_acc_trade_volume']
    
    # 날짜를 인덱스로 설정
    df = df.set_index('날짜')
    
    return df



