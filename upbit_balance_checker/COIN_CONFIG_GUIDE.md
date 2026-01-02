# 코인 및 시간 단위 설정 가이드

모든 전략의 코인과 시간 단위를 한 곳에서 쉽게 변경할 수 있습니다!

## 📍 설정 파일 위치

```
upbit_balance_checker/global_config.py
```

이 파일만 수정하면 모든 전략의 코인과 시간 단위가 변경됩니다.

## 🚀 빠른 사용법

### 1. 모든 전략의 코인을 한 번에 변경

`global_config.py` 파일을 열고 다음 부분을 수정하세요:

```python
# 기본 코인 (모든 전략에 적용)
DEFAULT_MARKET = 'KRW-BTC'  # 여기를 원하는 코인으로 변경
```

**예시:**
```python
DEFAULT_MARKET = 'KRW-ETH'   # 이더리움으로 변경
DEFAULT_MARKET = 'KRW-SOL'   # 솔라나로 변경
DEFAULT_MARKET = 'KRW-XRP'   # 리플로 변경
```

### 2. 특정 전략만 다른 코인 사용

`STRATEGY_MARKETS` 딕셔너리에서 특정 전략의 코인을 설정할 수 있습니다:

```python
STRATEGY_MARKETS = {
    'sma_5_20': None,           # None = DEFAULT_MARKET 사용
    'sma_20_50': None,          # None = DEFAULT_MARKET 사용
    'sma_minute': None,          # None = DEFAULT_MARKET 사용
    'macd': None,                # None = DEFAULT_MARKET 사용
    'momentum': 'KRW-XRP',       # XRP로 고정
    'goldcross_rsi': None,       # None = DEFAULT_MARKET 사용
}
```

**예시:**
```python
STRATEGY_MARKETS = {
    'sma_5_20': 'KRW-ETH',      # SMA 5/20만 이더리움 사용
    'momentum': 'KRW-SOL',       # 모멘텀 전략만 솔라나 사용
    'macd': None,                # 나머지는 DEFAULT_MARKET 사용
}
```

## 📋 사용 가능한 코인 목록

```python
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
```

## 💡 예시

### 예시 1: 모든 전략을 이더리움으로 변경

```python
# global_config.py
DEFAULT_MARKET = 'KRW-ETH'
```

### 예시 2: 기본은 비트코인, 모멘텀만 솔라나

```python
# global_config.py
DEFAULT_MARKET = 'KRW-BTC'

STRATEGY_MARKETS = {
    'momentum': 'KRW-SOL',  # 모멘텀만 솔라나
    # 나머지는 None (기본값 사용)
}
```

### 예시 3: 각 전략마다 다른 코인

```python
# global_config.py
DEFAULT_MARKET = 'KRW-BTC'  # 기본값 (사용 안 함)

STRATEGY_MARKETS = {
    'sma_5_20': 'KRW-ETH',
    'sma_20_50': 'KRW-SOL',
    'macd': 'KRW-XRP',
    'momentum': 'KRW-DOGE',
    'goldcross_rsi': 'KRW-ADA',
}
```

## ⚙️ 고급 사용법

Python 코드에서 직접 변경할 수도 있습니다:

```python
from global_config import set_default_market, set_strategy_market

# 모든 전략의 기본 코인 변경
set_default_market('KRW-ETH')

# 특정 전략의 코인 변경
set_strategy_market('momentum', 'KRW-SOL')
```

## ⏰ 시간 단위 설정

### 1. 모든 전략의 시간 단위를 한 번에 변경

```python
# 기본 시간 단위 (모든 전략에 적용)
DEFAULT_TIMEFRAME = 'daily'  # 👈 여기를 변경!
```

**사용 가능한 옵션:**
```python
DEFAULT_TIMEFRAME = 'daily'    # 일봉
DEFAULT_TIMEFRAME = '240min'    # 4시간봉
DEFAULT_TIMEFRAME = '60min'    # 1시간봉
DEFAULT_TIMEFRAME = '30min'    # 30분봉
DEFAULT_TIMEFRAME = '15min'    # 15분봉
DEFAULT_TIMEFRAME = '5min'     # 5분봉
DEFAULT_TIMEFRAME = '1min'     # 1분봉

# 또는 직접 분 단위 지정
DEFAULT_TIMEFRAME = 'minutes:240'  # 4시간봉 (240분)
DEFAULT_TIMEFRAME = 'minutes:60'   # 1시간봉 (60분)
```

### 2. 특정 전략만 다른 시간 단위 사용

```python
STRATEGY_TIMEFRAMES = {
    'sma_5_20': None,           # None = DEFAULT_TIMEFRAME 사용
    'sma_20_50': '60min',        # 1시간봉으로 설정
    'sma_minute': 'minutes:1',   # 1분봉
    'macd': 'minutes:240',       # 4시간봉
    'momentum': None,            # None = DEFAULT_TIMEFRAME 사용
    'goldcross_rsi': None,       # None = DEFAULT_TIMEFRAME 사용
}
```

### 3. 시간 단위 설정 예시

**예시 1: 모든 전략을 1시간봉으로 변경**
```python
DEFAULT_TIMEFRAME = '60min'
```

**예시 2: 기본은 일봉, MACD만 4시간봉**
```python
DEFAULT_TIMEFRAME = 'daily'

STRATEGY_TIMEFRAMES = {
    'macd': 'minutes:240',  # MACD만 4시간봉
    # 나머지는 None (일봉 사용)
}
```

**예시 3: 각 전략마다 다른 시간 단위**
```python
DEFAULT_TIMEFRAME = 'daily'  # 기본값

STRATEGY_TIMEFRAMES = {
    'sma_5_20': '60min',      # 1시간봉
    'sma_20_50': '240min',    # 4시간봉
    'sma_minute': '5min',     # 5분봉
    'macd': '30min',          # 30분봉
    'momentum': 'daily',      # 일봉
    'goldcross_rsi': '15min', # 15분봉
}
```

## 📝 참고사항

- 설정 변경 후 전략을 실행하면 새로운 코인과 시간 단위로 백테스트가 실행됩니다.
- 각 전략의 config 파일은 `global_config.py`를 자동으로 참조합니다.
- `None`으로 설정하면 `DEFAULT_MARKET` 또는 `DEFAULT_TIMEFRAME`을 사용합니다.
- 시간 단위 변경 시 `candles_count`도 자동으로 조정됩니다.

