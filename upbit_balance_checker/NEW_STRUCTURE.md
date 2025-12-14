# 🏗️ 새로운 프로젝트 구조

전략별로 폴더를 구성한 새로운 구조입니다.

## 📁 디렉토리 구조

```
upbit_balance_checker/
├── core/                        # 공통 모듈
│   ├── __init__.py
│   ├── indicators.py           # 기술적 지표 (SMA, RSI, etc)
│   ├── backtest_engine.py      # 백테스팅 엔진
│   └── data_fetcher.py         # 데이터 수집
│
├── strategies/                  # 전략 폴더
│   ├── __init__.py
│   │
│   ├── sma_strategy/           # SMA 골든크로스 전략 ⭐
│   │   ├── __init__.py
│   │   ├── config.py           # 전략 설정
│   │   ├── strategy.py         # 전략 구현
│   │   ├── run_sma5_20.py      # SMA 5/20 실행
│   │   ├── run_sma20_50.py     # SMA 20/50 실행
│   │   └── README.md
│   │
│   └── momentum_strategy/      # 모멘텀 전략 (예정) 🔜
│       ├── __init__.py
│       ├── config.py
│       ├── strategy.py
│       ├── run_momentum.py
│       └── README.md
│
├── config/                      # API 설정
│   ├── api_config.py
│   └── env_upbit.txt
│
├── utils/                       # 유틸리티
│   └── realtime_price_monitor.py
│
├── check_balance.py             # 잔고 조회
├── requirements.txt
└── README.md
```

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

### 2. 새 전략 추가 방법

```bash
# 1. 새 전략 폴더 생성
mkdir strategies/momentum_strategy

# 2. 필요한 파일 생성
strategies/momentum_strategy/
├── __init__.py
├── config.py          # 전략 설정
├── strategy.py        # 전략 구현
├── run_momentum.py    # 실행 파일
└── README.md

# 3. 전략 구현
# strategy.py에 전략 클래스 작성
# core 모듈의 indicators, backtest_engine 활용

# 4. 실행
cd strategies/momentum_strategy
python run_momentum.py
```

## 📦 core 모듈 사용법

### indicators.py
```python
from core.indicators import calculate_sma, calculate_rsi

# SMA 계산
df['sma20'] = calculate_sma(df, column='종가', window=20)

# RSI 계산
df['rsi'] = calculate_rsi(df, column='종가', period=14)
```

### backtest_engine.py
```python
from core.backtest_engine import BacktestEngine

engine = BacktestEngine(initial_cash=1_000_000, commission=0.0005)
result = engine.run(df, signals)
BacktestEngine.print_results(result)
```

### data_fetcher.py
```python
from core.data_fetcher import fetch_daily_data, fetch_minute_data

# 일봉 데이터
df = fetch_daily_data(market='KRW-BTC', days=365)

# 분봉 데이터
df = fetch_minute_data(market='KRW-BTC', minutes=5, count=1000)
```

## 🎯 전략 템플릿

새 전략을 만들 때 이 템플릿을 사용하세요:

```python
# strategies/your_strategy/strategy.py

import pandas as pd
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.indicators import calculate_sma, calculate_rsi
from core.backtest_engine import BacktestEngine


class YourStrategy:
    """당신의 전략 설명"""
    
    def __init__(self, param1, param2):
        self.param1 = param1
        self.param2 = param2
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        매매 신호 생성
        
        Returns
        -------
        pd.DataFrame
            'signal'과 'position' 컬럼 포함
        """
        # 신호 생성 로직
        signals = pd.DataFrame(index=df.index)
        signals['signal'] = 'HOLD'
        signals['position'] = 0
        
        # 매수/매도 신호 설정
        # signals.loc[buy_condition, 'signal'] = 'BUY'
        # signals.loc[buy_condition, 'position'] = 1
        
        return signals
    
    def get_statistics(self, df: pd.DataFrame) -> dict:
        """전략 통계 반환"""
        return {
            'strategy_name': '전략 이름',
            # 기타 통계...
        }
```

## 🔄 마이그레이션

기존 파일에서 새 구조로 이동:

| 기존 위치 | 새 위치 |
|-----------|---------|
| `strategy/indicators.py` | `core/indicators.py` |
| `strategy/backtest_engine.py` | `core/backtest_engine.py` |
| `run_sma5_20.py` | `strategies/sma_strategy/run_sma5_20.py` |
| `run_sma20_50.py` | `strategies/sma_strategy/run_sma20_50.py` |

## ✅ 장점

1. **전략별 독립성**: 각 전략이 독립적으로 관리됨
2. **확장 용이**: 새 전략 추가가 쉬움
3. **코드 재사용**: core 모듈 공통 사용
4. **명확한 구조**: 전략별로 폴더가 분리되어 찾기 쉬움
5. **유지보수**: 각 전략의 설정과 코드가 한 곳에 모여있음

## 🔜 다음 단계

1. ✅ SMA 전략 구현 완료
2. 🔜 20일 모멘텀 전략 추가
3. 🔜 RSI 기반 전략 추가
4. 🔜 멀티 타임프레임 전략 추가

