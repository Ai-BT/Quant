# ✨ 정리 완료된 프로젝트 구조

## 📁 최종 디렉토리 구조

```
upbit_balance_checker/
│
├── 📂 core/                          # 공통 모듈
│   ├── __init__.py
│   ├── indicators.py                # 기술적 지표 (SMA, RSI, etc)
│   ├── backtest_engine.py           # 백테스팅 엔진
│   └── data_fetcher.py              # 데이터 수집 (일봉/분봉)
│
├── 📂 strategies/                    # 전략별 폴더
│   ├── __init__.py
│   │
│   ├── 📂 sma_strategy/             # SMA 골든크로스 전략
│   │   ├── __init__.py
│   │   ├── config.py                # 전략 설정 (5/20, 20/50, 분봉)
│   │   ├── strategy.py              # SMA 전략 구현
│   │   ├── run_sma5_20.py          # SMA 5/20 실행
│   │   ├── run_sma20_50.py         # SMA 20/50 실행
│   │   └── README.md
│   │
│   └── 📂 goldcross_rsi_strategy/  # 골든크로스 + RSI 전략
│       ├── __init__.py
│       ├── config.py                # RSI 전략 설정
│       ├── strategy.py              # 전략 구현
│       ├── run_backtest.py          # 실행 파일
│       └── gold_cross_2050.ipynb    # 노트북 (참고용)
│
├── 📂 config/                        # API 설정
│   ├── __init__.py
│   ├── api_config.py                # API 설정 유틸
│   └── env_upbit.txt                # API 키 (gitignore됨)
│
├── 📄 check_balance.py              # 잔고 조회 유틸리티
├── 📄 realtime_monitor.py           # 실시간 가격 모니터링
├── 📄 requirements.txt
├── 📄 README.md
├── 📄 NEW_STRUCTURE.md              # 구조 설명
└── 📄 CLEAN_STRUCTURE.md            # 이 파일
```

## 🗑️ 삭제된 파일들

### 루트 폴더에서 삭제
- ❌ `run_sma5_20.py` → ✅ `strategies/sma_strategy/run_sma5_20.py`
- ❌ `run_sma20_50.py` → ✅ `strategies/sma_strategy/run_sma20_50.py`
- ❌ `run_sma_minute.py` → 나중에 재구현 예정
- ❌ `run_backtest.py` → ✅ `strategies/goldcross_rsi_strategy/run_backtest.py`

### config/ 폴더에서 삭제
- ❌ `sma5_20_config.py` → ✅ `strategies/sma_strategy/config.py` (통합)
- ❌ `sma20_50_config.py` → ✅ `strategies/sma_strategy/config.py` (통합)
- ❌ `sma_minute_config.py` → 나중에 재구현 예정
- ❌ `goldcross_rsi_config.py` → ✅ `strategies/goldcross_rsi_strategy/config.py`

### strategy/ 폴더 전체 삭제 (옛날 구조)
- ❌ `strategy/indicators.py` → ✅ `core/indicators.py`
- ❌ `strategy/backtest_engine.py` → ✅ `core/backtest_engine.py`
- ❌ `strategy/simple_golden_cross.py` → ✅ `strategies/sma_strategy/strategy.py`
- ❌ `strategy/golden_cross_rsi.py` → ✅ `strategies/goldcross_rsi_strategy/strategy.py`
- ❌ `strategy/gold_cross_2050.ipynb` → ✅ `strategies/goldcross_rsi_strategy/gold_cross_2050.ipynb`

### 기타
- ❌ `uitls/` 폴더 (오타) → 나중에 `utils/` 재생성 예정
- ❌ 모든 `__pycache__/` 폴더

## 🚀 사용 방법

### 1. SMA 전략 실행

```bash
# 프로젝트 루트에서
cd strategies/sma_strategy

# SMA 5/20 전략
python run_sma5_20.py

# SMA 20/50 전략
python run_sma20_50.py
```

### 2. 골든크로스 + RSI 전략 실행

```bash
cd strategies/goldcross_rsi_strategy
python run_backtest.py
```

### 3. 잔고 조회

```bash
# 루트 폴더에서
python check_balance.py
```

## ⚙️ 설정 변경

각 전략 폴더의 `config.py` 파일을 수정하세요:

```python
# strategies/sma_strategy/config.py
SMA5_20_CONFIG = {
    'market': 'KRW-ETH',      # 코인 변경
    'fast_period': 5,
    'slow_period': 20,
    'initial_cash': 1_000_000,
}

# strategies/goldcross_rsi_strategy/config.py
FAST_PERIOD = 20
SLOW_PERIOD = 50
RSI_PERIOD = 14
MARKET = 'KRW-BTC'
```

## 📦 패키지 구조

```python
# core 모듈 사용
from core.indicators import calculate_sma, calculate_rsi
from core.backtest_engine import BacktestEngine
from core.data_fetcher import fetch_daily_data, fetch_minute_data

# 전략 사용
from strategies.sma_strategy.strategy import SMAStrategy
from strategies.goldcross_rsi_strategy.strategy import GoldenCrossRSIStrategy
```

## ✅ 정리 효과

1. ✨ **명확한 구조**: 전략별로 독립된 폴더
2. 🔧 **유지보수 용이**: 각 전략의 코드와 설정이 한 곳에
3. 🚀 **확장 용이**: 새 전략 추가가 쉬움
4. ♻️ **코드 재사용**: core 모듈 공통 사용
5. 🧹 **깔끔함**: 중복 파일 제거, 불필요한 파일 정리

## 🔜 다음 단계

### 추가 예정 전략
```
strategies/
├── momentum_strategy/      # 20일 모멘텀 전략
├── rsi_strategy/          # RSI 기반 전략
├── bollinger_strategy/    # 볼린저 밴드 전략
└── multi_timeframe/       # 멀티 타임프레임 전략
```

### 유틸리티 추가
```
utils/
├── realtime_price_monitor.py  # 실시간 가격 모니터링
├── notification.py            # 알림 기능
└── risk_management.py         # 리스크 관리
```

## 📝 참고

- 모든 전략은 독립적으로 실행 가능
- `core/` 모듈은 모든 전략에서 공통으로 사용
- 각 전략 폴더에는 README.md 작성 권장
- API 키는 `config/env_upbit.txt`에 보관 (gitignore됨)

