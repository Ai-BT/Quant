"""
모멘텀 전략 설정 파일

다양한 모멘텀 전략 설정을 정의
"""

import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from global_config import get_market, get_candles_count, INITIAL_CASH, COMMISSION

# ============================================
# 20일 모멘텀 전략 설정
# ============================================
MOMENTUM_20_CONFIG = {
    'name': '20일 모멘텀 전략',
    'lookback_period': 20,        # 모멘텀 계산 기간 (일)
    'buy_threshold': 0.05,        # 매수 기준: 5% 이상 상승
    'sell_threshold': -0.03,      # 매도 기준: -3% 이하 하락
    'initial_cash': INITIAL_CASH,
    'commission': COMMISSION,
    'market': get_market('momentum'),  # global_config에서 가져옴
    'candles_count': get_candles_count('daily'),
}

# ============================================
# 10일 모멘텀 전략 설정 (단기)
# ============================================
MOMENTUM_10_CONFIG = {
    'name': '10일 모멘텀 전략 (단기)',
    'lookback_period': 10,        # 10일 모멘텀
    'buy_threshold': 0.03,        # 매수 기준: 3% 이상
    'sell_threshold': -0.02,      # 매도 기준: -2% 이하
    'initial_cash': INITIAL_CASH,
    'commission': COMMISSION,
    'market': get_market('momentum'),
    'candles_count': get_candles_count('daily'),
}

# ============================================
# 30일 모멘텀 전략 설정 (중장기)
# ============================================
MOMENTUM_30_CONFIG = {
    'name': '30일 모멘텀 전략 (중장기)',
    'lookback_period': 30,        # 30일 모멘텀
    'buy_threshold': 0.08,        # 매수 기준: 8% 이상
    'sell_threshold': -0.05,      # 매도 기준: -5% 이하
    'initial_cash': INITIAL_CASH,
    'commission': COMMISSION,
    'market': get_market('momentum'),
    'candles_count': get_candles_count('daily'),
}

# ============================================
# 듀얼 모멘텀 전략 설정 (상대 강도 + 절대 모멘텀)
# ============================================
DUAL_MOMENTUM_CONFIG = {
    'name': '듀얼 모멘텀 전략',
    'lookback_period': 20,        # 모멘텀 계산 기간
    'buy_threshold': 0.0,         # 매수 기준: 0% 이상 (상승만)
    'sell_threshold': 0.0,        # 매도 기준: 0% 이하 (하락 시)
    'initial_cash': INITIAL_CASH,
    'commission': COMMISSION,
    'market': get_market('momentum'),
    'candles_count': get_candles_count('daily'),
}

