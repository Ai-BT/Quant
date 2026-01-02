"""
SMA 전략 설정 파일

여러 SMA 전략의 기본 설정값들을 정의
"""

# ============================================
# SMA 5/20 전략 설정 (일봉)
# ============================================
SMA5_20_CONFIG = {
    'name': 'SMA 5/20 골든크로스 (일봉)',
    'fast_period': 5,
    'slow_period': 20,
    'initial_cash': 1_000_000,
    'commission': 0.0005,
    'market': 'KRW-BTC',
    'candle_type': 'days',
    'candles_count': 365,
}

# ============================================
# SMA 20/50 전략 설정 (일봉)
# ============================================
SMA20_50_CONFIG = {
    'name': 'SMA 20/50 골든크로스 (일봉)',
    'fast_period': 20,
    'slow_period': 50,
    'initial_cash': 1_000_000,
    'commission': 0.0005,
    'market': 'KRW-BTC',
    'candle_type': 'days',
    'candles_count': 365,
}

# ============================================
# SMA 5/30 전략 설정 (분봉)
# ============================================
SMA_MINUTE_CONFIG = {
    'name': 'SMA 5분/30분 골든크로스 (분봉)',
    'fast_period': 5,
    'slow_period': 30,
    'trade_interval': 60,  # 거래 확인 간격 (분)
    'initial_cash': 1_000_000,
    'commission': 0.0005,
    'market': 'KRW-BTC',
    'candle_type': 'minutes',
    'candle_minutes': 1,
    'candles_count': 1000,
}

