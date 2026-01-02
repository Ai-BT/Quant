"""
SOL SMA 전략 설정
"""

# 전략 설정
STRATEGY_CONFIG = {
    'name': 'SOL SMA 골든크로스 전략',
    'market': 'KRW-SOL',
    'fast_period': 5,  # 단기 이동평균
    'slow_period': 20,  # 장기 이동평균
    'check_interval': 300,  # 5분마다 체크 (초 단위)
    'buy_amount_ratio': 0.1,  # 잔고의 10%씩 매수
    'sell_all_on_signal': True,  # 매도 신호 시 전량 매도
}


