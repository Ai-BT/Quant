"""
SMA 전략 설정 파일

여러 SMA 전략의 기본 설정값들을 정의
"""

import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from global_config import get_market, get_timeframe, get_candles_count, INITIAL_CASH, COMMISSION

# ============================================
# SMA 5/20 전략 설정
# ============================================
def _get_sma5_20_config():
    """SMA 5/20 전략 설정 (global_config에서 시간 단위 가져옴)"""
    timeframe = get_timeframe('sma_5_20')
    config = {
        'name': 'SMA 5/20 골든크로스',
        'fast_period': 5,
        'slow_period': 20,
        'initial_cash': INITIAL_CASH,
        'commission': COMMISSION,
        'market': get_market('sma_5_20'),
    }
    
    if timeframe['type'] == 'daily':
        config['candle_type'] = 'days'
        config['candles_count'] = 365
        config['name'] += ' (일봉)'
    else:
        config['candle_type'] = 'minutes'
        config['candle_minutes'] = timeframe['minutes']
        config['candles_count'] = 1000
        config['name'] += f" ({timeframe['description']})"
    
    return config

# 함수로 export하여 매번 최신 설정을 가져오도록 함
def get_sma5_20_config():
    """SMA 5/20 전략 설정 (매번 최신 global_config에서 가져옴)"""
    return _get_sma5_20_config()

# 하위 호환성을 위한 변수 (함수 호출로 동적 생성)
class _ConfigProxy:
    """동적으로 config를 가져오는 프록시 클래스"""
    def __init__(self, getter_func):
        self._getter = getter_func
    
    def __getitem__(self, key):
        return self._getter()[key]
    
    def __contains__(self, key):
        return key in self._getter()
    
    def get(self, key, default=None):
        return self._getter().get(key, default)
    
    def __iter__(self):
        return iter(self._getter())
    
    def keys(self):
        return self._getter().keys()
    
    def values(self):
        return self._getter().values()
    
    def items(self):
        return self._getter().items()
    
    def __repr__(self):
        return repr(self._getter())

SMA5_20_CONFIG = _ConfigProxy(_get_sma5_20_config)

# ============================================
# SMA 20/50 전략 설정
# ============================================
def _get_sma20_50_config():
    """SMA 20/50 전략 설정 (global_config에서 시간 단위 가져옴)"""
    timeframe = get_timeframe('sma_20_50')
    config = {
        'name': 'SMA 20/50 골든크로스',
        'fast_period': 20,
        'slow_period': 50,
        'initial_cash': INITIAL_CASH,
        'commission': COMMISSION,
        'market': get_market('sma_20_50'),
    }
    
    if timeframe['type'] == 'daily':
        config['candle_type'] = 'days'
        config['candles_count'] = get_candles_count('daily')
        config['name'] += ' (일봉)'
    else:
        config['candle_type'] = 'minutes'
        config['candle_minutes'] = timeframe['minutes']
        config['candles_count'] = get_candles_count('minutes')
        config['name'] += f" ({timeframe['description']})"
    
    return config

def get_sma20_50_config():
    """SMA 20/50 전략 설정 (매번 최신 global_config에서 가져옴)"""
    return _get_sma20_50_config()

# 하위 호환성을 위한 변수 (함수 호출로 동적 생성)
SMA20_50_CONFIG = _ConfigProxy(_get_sma20_50_config)

# ============================================
# SMA 5/30 전략 설정 (분봉)
# ============================================
def _get_sma_minute_config():
    """SMA 분봉 전략 설정 (global_config에서 시간 단위 가져옴)"""
    timeframe = get_timeframe('sma_minute')
    config = {
        'name': 'SMA 5분/30분 골든크로스',
        'fast_period': 5,
        'slow_period': 30,
        'trade_interval': 60,  # 거래 확인 간격 (분)
        'initial_cash': INITIAL_CASH,
        'commission': COMMISSION,
        'market': get_market('sma_minute'),
    }
    
    if timeframe['type'] == 'daily':
        config['candle_type'] = 'days'
        config['candles_count'] = get_candles_count('daily')
        config['name'] += ' (일봉)'
    else:
        config['candle_type'] = 'minutes'
        config['candle_minutes'] = timeframe['minutes']
        config['candles_count'] = get_candles_count('minutes')
        config['name'] += f" ({timeframe['description']})"
    
    return config

def get_sma_minute_config():
    """SMA 분봉 전략 설정 (매번 최신 global_config에서 가져옴)"""
    return _get_sma_minute_config()

# 하위 호환성을 위한 변수 (함수 호출로 동적 생성)
SMA_MINUTE_CONFIG = _ConfigProxy(_get_sma_minute_config)

