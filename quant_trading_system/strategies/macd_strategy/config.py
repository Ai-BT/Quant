"""
MACD + Trend Filter 전략 설정

실시간 실행을 위한 설정
"""

# 전략 설정
STRATEGY_CONFIG = {
    'name': 'MACD Trend Filter 전략',
    'market': 'KRW-SOL',
    
    # MACD 설정
    'macd_fast': 12,              # MACD 단기 EMA
    'macd_slow': 26,              # MACD 장기 EMA
    'macd_signal': 9,             # Signal Line EMA
    
    # Trend Filter 설정
    'trend_ma_period': 200,       # 추세 확인용 이동평균 (200일 SMA)
    'trend_ma_type': 'SMA',       # 'SMA' or 'EMA'
    'use_trend_filter': True,     # Trend Filter 사용 여부
    
    # 추가 필터
    'use_histogram_filter': True,  # Histogram > 0 조건 사용 여부
    'min_histogram': 0,           # 최소 Histogram 값
    'use_dual_trend': False,      # 이중 트렌드 필터 사용 여부
    'use_volume_filter': False,   # 거래량 필터 사용 여부
    
    # 실시간 실행 설정
    'check_interval': 3600,       # 1시간마다 체크 (초 단위) - 1시간봉 데이터
    'buy_amount_ratio': 0.1,      # 잔고의 10%씩 매수
    'sell_all_on_signal': True,   # 매도 신호 시 전량 매도
    'candle_minutes': 60,         # 1시간봉 사용
}

