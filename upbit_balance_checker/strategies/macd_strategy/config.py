"""
MACD + Trend Filter 전략 설정

MACD (Moving Average Convergence Divergence):
- 단기/장기 이동평균의 차이로 모멘텀 파악
- Signal Line과의 교차로 매매 시점 포착

Trend Filter:
- 장기 이동평균선으로 큰 추세 방향 확인
- 추세에 순응하는 매매만 허용
"""

# ============================================================================
# MACD + 200일 SMA Trend Filter (추천) - 일봉
# ============================================================================
MACD_TREND_CONFIG = {
    'name': 'MACD_Trend_Filter',

    # MACD 설정
    'macd_fast': 12,              # MACD 단기 EMA (일반적으로 12)
    'macd_slow': 26,              # MACD 장기 EMA (일반적으로 26)
    'macd_signal': 9,             # Signal Line EMA (일반적으로 9)

    # Trend Filter 설정
    'trend_ma_period': 200,       # 추세 확인용 이동평균 (200일 SMA)
    'trend_ma_type': 'SMA',       # 'SMA' or 'EMA'

    # 추가 필터 (선택)
    'use_histogram_filter': True,  # Histogram > 0 조건 사용 여부
    'min_histogram': 0,           # 최소 Histogram 값

    # 백테스팅 설정
    'initial_cash': 1_000_000,
    'commission': 0.0005,
    'market': 'KRW-BTC',  # BTC, XRP, ETH, SOL, DOGE, ADA, DOT, LTC, BCH, XLM, LINK, XMR, EOS, ETC

    # 데이터 설정
    'timeframe': 'daily',         # 'daily', 'minute'
    'candles_count': 500,         # 최소 200일 이상 필요
}


# ============================================================================
# MACD + 50/200 이중 트렌드 필터 (보수적)
# ============================================================================
MACD_DUAL_TREND_CONFIG = {
    'name': 'MACD_Dual_Trend_Filter',

    # MACD 설정
    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9,

    # Trend Filter 설정
    'trend_ma_period': 200,       # 장기 추세
    'trend_ma_type': 'SMA',
    'use_dual_trend': True,       # 이중 필터 사용
    'mid_trend_period': 50,       # 중기 추세

    # 추가 필터
    'use_histogram_filter': True,
    'min_histogram': 0,

    # 백테스팅 설정
    'initial_cash': 1_000_000,
    'commission': 0.0005,
    'market': 'KRW-BTC',
    'candles_count': 500,
}


# ============================================================================
# MACD + Volume Filter (거래량 필터 추가)
# ============================================================================
MACD_VOLUME_CONFIG = {
    'name': 'MACD_Volume_Filter',

    # MACD 설정
    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9,

    # Trend Filter 설정
    'trend_ma_period': 200,
    'trend_ma_type': 'SMA',

    # Volume Filter 설정
    'use_volume_filter': True,
    'volume_ma_period': 20,       # 거래량 이동평균 기간
    'volume_multiplier': 1.2,     # 평균 거래량 대비 배수

    # 추가 필터
    'use_histogram_filter': True,
    'min_histogram': 0,

    # 백테스팅 설정
    'initial_cash': 1_000_000,
    'commission': 0.0005,
    'market': 'KRW-BTC',
    'candles_count': 500,
}


# ============================================================================
# MACD 단독 (비교용 - Trend Filter 없음)
# ============================================================================
MACD_ONLY_CONFIG = {
    'name': 'MACD_Only',

    # MACD 설정
    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9,

    # Trend Filter 비활성화
    'use_trend_filter': False,

    # 추가 필터
    'use_histogram_filter': False,

    # 백테스팅 설정
    'initial_cash': 1_000_000,
    'commission': 0.0005,
    'market': 'KRW-BTC',

    # 데이터 설정
    'timeframe': 'daily',
    'candles_count': 365,
}


# ============================================================================
# MACD + Trend Filter - 15분봉
# ============================================================================
MACD_15MIN_CONFIG = {
    'name': 'MACD_Trend_15min',

    # MACD 설정
    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9,

    # Trend Filter 설정
    'trend_ma_period': 200,       # 200개 = 50시간 = 약 2일
    'trend_ma_type': 'SMA',

    # 추가 필터
    'use_histogram_filter': True,
    'min_histogram': 0,

    # 백테스팅 설정
    'initial_cash': 1_000_000,
    'commission': 0.0005,
    'market': 'KRW-BTC',

    # 데이터 설정
    'timeframe': 'minute',
    'candle_minutes': 15,         # 15분봉
    'candles_count': 1000,        # 1000개 = 250시간 = 약 10일
}


# ============================================================================
# MACD + Trend Filter - 30분봉
# ============================================================================
MACD_30MIN_CONFIG = {
    'name': 'MACD_Trend_30min',

    # MACD 설정
    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9,

    # Trend Filter 설정
    'trend_ma_period': 200,       # 200개 = 100시간 = 약 4일
    'trend_ma_type': 'SMA',

    # 추가 필터
    'use_histogram_filter': True,
    'min_histogram': 0,

    # 백테스팅 설정
    'initial_cash': 1_000_000,
    'commission': 0.0005,
    'market': 'KRW-BTC',

    # 데이터 설정
    'timeframe': 'minute',
    'candle_minutes': 30,         # 30분봉
    'candles_count': 1000,        # 1000개 = 500시간 = 약 20일
}


# ============================================================================
# MACD + Trend Filter - 1시간봉
# ============================================================================
MACD_1HOUR_CONFIG = {
    'name': 'MACD_Trend_1hour',

    # MACD 설정
    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9,

    # Trend Filter 설정
    'trend_ma_period': 200,       # 200개 = 200시간 = 약 8일
    'trend_ma_type': 'SMA',

    # 추가 필터
    'use_histogram_filter': True,
    'min_histogram': 0,

    # 백테스팅 설정
    'initial_cash': 1_000_000,
    'commission': 0.0005,
    'market': 'KRW-BTC',

    # 데이터 설정
    'timeframe': 'minute',
    'candle_minutes': 60,         # 1시간봉
    'candles_count': 1000,        # 1000개 = 1000시간 = 약 41일
}


# ============================================================================
# MACD + Trend Filter - 4시간봉
# ============================================================================
MACD_4HOUR_CONFIG = {
    'name': 'MACD_Trend_4hour',

    # MACD 설정
    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9,

    # Trend Filter 설정
    'trend_ma_period': 200,       # 200개 = 800시간 = 약 33일
    'trend_ma_type': 'SMA',

    # 추가 필터
    'use_histogram_filter': True,
    'min_histogram': 0,

    # 백테스팅 설정
    'initial_cash': 1_000_000,
    'commission': 0.0005,
    'market': 'KRW-SOL',

    # 데이터 설정
    'timeframe': 'minute',
    'candle_minutes': 240,        # 4시간봉
    'candles_count': 1000,        # 1000개 = 4000시간 = 약 166일
}


# ============================================================================
# MACD + Trend Filter - 1분봉
# ============================================================================
MACD_1MIN_CONFIG = {
    'name': 'MACD_Trend_1min',

    # MACD 설정
    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9,

    # Trend Filter 설정
    'trend_ma_period': 200,       # 200개 = 200분 = 약 3.3시간
    'trend_ma_type': 'SMA',

    # 추가 필터
    'use_histogram_filter': True,
    'min_histogram': 0,

    # 백테스팅 설정
    'initial_cash': 1_000_000,
    'commission': 0.0005,
    'market': 'KRW-BTC',

    # 데이터 설정
    'timeframe': 'minute',
    'candle_minutes': 1,          # 1분봉
    'candles_count': 1000,        # 1000개 = 1000분 = 약 16시간
}
