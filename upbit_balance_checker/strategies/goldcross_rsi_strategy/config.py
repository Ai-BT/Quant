"""
백테스트 설정

변경 가능한 설정값들
"""

import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from global_config import get_market, INITIAL_CASH, COMMISSION

# ============================================
# 전략 설정
# ============================================

# 이동평균선 설정
FAST_PERIOD = 20      # 단기 이동평균 기간
SLOW_PERIOD = 50      # 장기 이동평균 기간

# RSI 설정
RSI_PERIOD = 14       # RSI 계산 기간
RSI_BUY_THRESHOLD = 50.0   # 매수 시 RSI 최대값 (이 값 이하일 때만 매수)
RSI_SELL_THRESHOLD = 70.0  # 매도 시 RSI 최소값 (이 값 이상일 때만 매도)

# ============================================
# 백테스트 설정
# ============================================

# INITIAL_CASH와 COMMISSION은 global_config에서 가져옴

# ============================================
# 데이터 수집 설정
# ============================================

MARKET = get_market('goldcross_rsi')  # global_config에서 가져옴
DAYS = 365            # 수집할 일수 (1년)

