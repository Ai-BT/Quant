"""
전역 설정 파일

모든 전략에서 공통으로 사용하는 설정값들
이 파일만 수정하면 모든 전략의 코인과 시간 단위를 한 번에 변경할 수 있습니다.
"""

# ============================================
# ⚙️ 주요 설정 (여기서 변경하면 모든 전략에 적용)
# ============================================

# 기본 코인 (모든 전략에 적용)
# 옵션: 'KRW-BTC', 'KRW-ETH', 'KRW-XRP', 'KRW-SOL', 'KRW-DOGE', 'KRW-ADA', 'KRW-DOT', 'KRW-LTC', 'KRW-BCH', 'KRW-XLM', 'KRW-LINK', 'KRW-XMR', 'KRW-EOS', 'KRW-ETC'
DEFAULT_MARKET = 'KRW-SOL'

# 기본 시간 단위 (모든 전략에 적용)
# 옵션: 'daily', '240min', '60min', '30min', '15min', '5min', '1min'
DEFAULT_TIMEFRAME = '240min'  # 1시간봉

# 기본 캔들 개수 (모든 전략에 적용)
# 일봉: 일봉 데이터 개수, 분봉: 모든 분봉(4시간/1시간/30분/15분/5분/1분) 데이터 개수
DEFAULT_CANDLES_COUNT = {
    'daily': 365,      # 일봉: 365개 (약 1년)
    'minutes': 2000,   # 분봉: 1000개
}

# 초기 자본금
INITIAL_CASH = 1_000_000      # 100만원

# 수수료율
COMMISSION = 0.0005          # 0.05%

# ============================================
# 전략별 상세 설정 (일반적으로 수정 불필요)
# ============================================

# 전략별 코인 설정 (None이면 DEFAULT_MARKET 사용)
STRATEGY_MARKETS = {
    'sma_5_20': None,           # None = DEFAULT_MARKET 사용
    'sma_20_50': None,          # None = DEFAULT_MARKET 사용
    'macd': None,                # None = DEFAULT_MARKET 사용
    'momentum': None,            # None = DEFAULT_MARKET 사용
    'goldcross_rsi': None,       # None = DEFAULT_MARKET 사용
}

# 전략별 시간 단위 설정 (None이면 DEFAULT_TIMEFRAME 사용)
# 값 형식: 'daily' 또는 'minutes:숫자' (예: 'minutes:240' = 4시간봉)
STRATEGY_TIMEFRAMES = {
    'sma_5_20': None,           # None = DEFAULT_TIMEFRAME 사용
    'sma_20_50': None,          # None = DEFAULT_TIMEFRAME 사용
    'macd': None,               # None = DEFAULT_TIMEFRAME 사용
    'momentum': None,            # None = DEFAULT_TIMEFRAME 사용
    'goldcross_rsi': None,      # None = DEFAULT_TIMEFRAME 사용
}

# 사용 가능한 시간 단위
AVAILABLE_TIMEFRAMES = {
    'daily': {'type': 'daily', 'minutes': None, 'description': '일봉'},
    '240min': {'type': 'minutes', 'minutes': 240, 'description': '4시간봉'},
    '60min': {'type': 'minutes', 'minutes': 60, 'description': '1시간봉'},
    '30min': {'type': 'minutes', 'minutes': 30, 'description': '30분봉'},
    '15min': {'type': 'minutes', 'minutes': 15, 'description': '15분봉'},
    '5min': {'type': 'minutes', 'minutes': 5, 'description': '5분봉'},
    '1min': {'type': 'minutes', 'minutes': 1, 'description': '1분봉'},
}

# ============================================
# 사용 가능한 코인 목록
# ============================================

AVAILABLE_MARKETS = [
    'KRW-BTC',   # 비트코인
    'KRW-ETH',   # 이더리움
    'KRW-XRP',   # 리플
    'KRW-SOL',   # 솔라나
    'KRW-DOGE',  # 도지코인
    'KRW-ADA',   # 에이다
    'KRW-DOT',   # 폴카닷
    'KRW-LTC',   # 라이트코인
    'KRW-BCH',   # 비트코인캐시
    'KRW-XLM',   # 스텔라루멘
    'KRW-LINK',  # 체인링크
    'KRW-XMR',   # 모네로
    'KRW-EOS',   # 이오스
    'KRW-ETC',   # 이더리움클래식
]

# ============================================
# 헬퍼 함수
# ============================================

def get_market(strategy_name: str) -> str:
    """
    전략별 코인 반환
    
    Parameters
    ----------
    strategy_name : str
        전략 이름 (예: 'sma_5_20', 'momentum')
    
    Returns
    -------
    str
        마켓 코드 (예: 'KRW-BTC')
    """
    market = STRATEGY_MARKETS.get(strategy_name)
    return market if market is not None else DEFAULT_MARKET


def set_default_market(market: str):
    """
    기본 코인 변경
    
    Parameters
    ----------
    market : str
        마켓 코드 (예: 'KRW-BTC')
    """
    global DEFAULT_MARKET
    if market not in AVAILABLE_MARKETS:
        raise ValueError(f"지원하지 않는 마켓입니다: {market}")
    DEFAULT_MARKET = market
    print(f"✅ 기본 코인을 {market}로 변경했습니다.")


def set_strategy_market(strategy_name: str, market: str):
    """
    특정 전략의 코인 변경
    
    Parameters
    ----------
    strategy_name : str
        전략 이름
    market : str
        마켓 코드
    """
    if market not in AVAILABLE_MARKETS:
        raise ValueError(f"지원하지 않는 마켓입니다: {market}")
    STRATEGY_MARKETS[strategy_name] = market
    print(f"✅ {strategy_name} 전략의 코인을 {market}로 변경했습니다.")


def get_timeframe(strategy_name: str) -> dict:
    """
    전략별 시간 단위 반환
    
    Parameters
    ----------
    strategy_name : str
        전략 이름 (예: 'sma_5_20', 'macd')
    
    Returns
    -------
    dict
        시간 단위 정보
        {
            'type': 'daily' or 'minutes',
            'minutes': int or None,
            'description': str
        }
    """
    timeframe_str = STRATEGY_TIMEFRAMES.get(strategy_name)
    
    # None이면 기본값 사용
    if timeframe_str is None:
        timeframe_str = DEFAULT_TIMEFRAME
    
    # 'daily'인 경우
    if timeframe_str == 'daily':
        return {
            'type': 'daily',
            'minutes': None,
            'description': '일봉'
        }
    
    # 'minutes:숫자' 형식인 경우
    if timeframe_str.startswith('minutes:'):
        minutes = int(timeframe_str.split(':')[1])
        return {
            'type': 'minutes',
            'minutes': minutes,
            'description': f'{minutes}분봉'
        }
    
    # 미리 정의된 키워드인 경우
    if timeframe_str in AVAILABLE_TIMEFRAMES:
        return AVAILABLE_TIMEFRAMES[timeframe_str].copy()
    
    # 기본값 반환
    return {
        'type': 'daily',
        'minutes': None,
        'description': '일봉'
    }


def set_default_timeframe(timeframe: str):
    """
    기본 시간 단위 변경
    
    Parameters
    ----------
    timeframe : str
        시간 단위 ('daily', '240min', '60min', '30min', '15min', '5min', '1min')
        또는 'minutes:숫자' 형식
    """
    global DEFAULT_TIMEFRAME
    DEFAULT_TIMEFRAME = timeframe
    print(f"✅ 기본 시간 단위를 {timeframe}로 변경했습니다.")


def set_strategy_timeframe(strategy_name: str, timeframe: str):
    """
    특정 전략의 시간 단위 변경
    
    Parameters
    ----------
    strategy_name : str
        전략 이름
    timeframe : str
        시간 단위 ('daily', '240min', '60min', '30min', '15min', '5min', '1min')
        또는 'minutes:숫자' 형식
    """
    STRATEGY_TIMEFRAMES[strategy_name] = timeframe
    print(f"✅ {strategy_name} 전략의 시간 단위를 {timeframe}로 변경했습니다.")


def get_candles_count(timeframe_type: str) -> int:
    """
    시간 단위에 따른 기본 캔들 개수 반환
    
    Parameters
    ----------
    timeframe_type : str
        시간 단위 타입 ('daily' 또는 'minutes')
    
    Returns
    -------
    int
        캔들 개수
    """
    return DEFAULT_CANDLES_COUNT.get(timeframe_type, DEFAULT_CANDLES_COUNT['minutes'])

