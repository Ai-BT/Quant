"""
MACD 실시간 거래 설정

MACD + Trend Filter 전략 설정값들
"""

# ============================================
# MACD 전략 설정
# ============================================

# MACD 설정
MACD_FAST = 12              # MACD 단기 EMA 기간
MACD_SLOW = 26              # MACD 장기 EMA 기간
MACD_SIGNAL = 9             # Signal Line EMA 기간

# Trend Filter 설정
USE_TREND_FILTER = True     # Trend Filter 사용 여부
TREND_MA_PERIOD = 200       # 추세 확인용 이동평균 기간
TREND_MA_TYPE = 'SMA'       # 'SMA' or 'EMA'

# Histogram Filter 설정
USE_HISTOGRAM_FILTER = True  # Histogram 필터 사용 여부
MIN_HISTOGRAM = 0           # 최소 Histogram 값

# 이중 트렌드 필터 (선택)
USE_DUAL_TREND = False      # 이중 트렌드 필터 사용 여부
MID_TREND_PERIOD = 50       # 중기 트렌드 MA 기간

# Volume Filter 설정 (선택)
USE_VOLUME_FILTER = False   # 거래량 필터 사용 여부
VOLUME_MA_PERIOD = 20       # 거래량 이동평균 기간
VOLUME_MULTIPLIER = 1.2     # 평균 거래량 대비 배수

# ============================================
# 가상 거래 설정
# ============================================

INITIAL_CASH = 1_000_000  # 초기 자본금 (100만원)
COMMISSION = 0.0005        # 수수료율 (0.05%)

# ============================================
# 거래 설정
# ============================================

MARKET = 'KRW-BTC'    # 거래할 마켓
INTERVAL = 60         # 체크 주기 (초) - 1분마다 체크
CANDLE_MINUTES = 1    # 분봉 단위 (1, 3, 5, 10, 15, 30, 60, 240)
CANDLE_COUNT = 300    # 수집할 캔들 개수 (최소 TREND_MA_PERIOD보다 커야 함)

# ============================================
# 로깅 설정
# ============================================

LOG_DIR = 'logs'      # 로그 파일 디렉토리
SAVE_TRADES = True    # 거래 내역 저장 여부
