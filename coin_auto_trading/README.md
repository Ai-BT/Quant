# 코인 자동매매 시스템

24시간 자동매매 시스템 (MVP: Paper Trading)

## 핵심 원칙

- **백테스트와 라이브가 동일한 DecisionEngine 사용**
- **상태 머신 명확한 구현** (FLAT/LONG/PENDING)
- **멀티 타임프레임 지원** (15m, 1h 등), 판단은 캔들 마감 이벤트에서만
- **모든 결정 DB 기록** (시그널/피처/액션/포지션/주문)
- **중복 주문 방지** (idempotency)
- **작동하는 최소 단위부터 구현**, 각 단계마다 실행 가능한 CLI 제공
- **안정성/재현성/로그 우선**

## 프로젝트 구조

```
coin_auto_trading/
├── app/
│   ├── core/           # 핵심 모듈 (상태 머신, DB, 로거)
│   ├── data/           # 캔들 데이터 관리
│   ├── features/       # 기술적 지표 (SMA, MACD, RSI 등)
│   ├── strategies/     # 트레이딩 전략
│   ├── decision/       # 결정 엔진 (백테스트/라이브 공통)
│   ├── execution/      # 주문 실행, 중복 방지
│   ├── backtest/       # 백테스트 엔진
│   ├── api/            # 거래소 API (Mock/Upbit)
│   └── ops/            # 모니터링, 알림
├── tests/              # 테스트 코드
├── db/                 # SQLite DB 파일
├── logs/               # 로그 파일
├── cli.py              # CLI 도구
├── requirements.txt    # 의존성
└── README.md
```

## 설치

```bash
# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일 수정 (API 키 등)
```

## 사용법

### 1. 백테스트 실행

```bash
# 기본 백테스트 (SMA 전략)
python cli.py backtest --strategy sma --symbol KRW-BTC --timeframe 15m

# 옵션 지정
python cli.py backtest \
  --strategy sma \
  --symbol KRW-BTC \
  --timeframe 15m \
  --fast-period 5 \
  --slow-period 20 \
  --initial-cash 1000000 \
  --days 30 \
  --db  # DB에 기록
```

### 2. 라이브 트레이딩 (Paper Trading)

```bash
python cli.py live --strategy sma --symbol KRW-BTC
```

### 3. DB 상태 확인

```bash
python cli.py check-db
```

## 핵심 모듈

### 상태 머신 (app/core/state_machine.py)

포지션 상태 관리:
- `FLAT`: 포지션 없음
- `LONG`: 매수 포지션 보유
- `PENDING`: 주문 대기 중

### Decision Engine (app/decision/engine.py)

백테스트와 라이브에서 공통으로 사용하는 결정 엔진:
- 캔들 마감 이벤트에서만 판단
- 전략으로부터 시그널 생성
- 모든 결정을 DB에 기록

### 백테스트 엔진 (app/backtest/engine.py)

DecisionEngine을 사용하여 백테스트 실행:
- 실제 거래 시뮬레이션
- 수수료, 슬리피지 고려
- 성과 지표 계산

### 실행 모듈 (app/execution/executor.py)

주문 실행 및 중복 방지:
- idempotency 보장 (주문 ID 중복 확인)
- Paper Trading 지원 (Mock API)
- 모든 주문을 DB에 기록

## 전략 추가

`app/strategies/` 디렉토리에 새 전략을 추가:

```python
from app.strategies.base_strategy import BaseStrategy
from app.data.candle import Candle, Timeframe
from app.core.state_machine import PositionState

class MyStrategy(BaseStrategy):
    def generate_signal(self, candles, current_state, features=None):
        # 전략 로직 구현
        return {
            'action': 'BUY',  # 또는 'SELL', 'HOLD'
            'confidence': 0.8,
            'reason': 'Signal reason',
            'metadata': {}
        }
```

## 데이터베이스 스키마

- **signals**: 시그널 기록
- **actions**: 액션 기록
- **positions**: 포지션 기록
- **orders**: 주문 기록 (idempotency)

## 테스트

```bash
pytest tests/
```

## 개발 로드맵

- [x] 기본 프로젝트 구조
- [x] 상태 머신 구현
- [x] DecisionEngine 구현
- [x] 백테스트 엔진 (기본)
- [x] Paper Trading (Mock API)
- [x] DB 스키마 및 기록
- [x] CLI 도구
- [ ] 실제 거래소 API 연동 (Upbit)
- [ ] 실시간 캔들 데이터 수신
- [ ] 멀티 타임프레임 정확한 캔들 마감 이벤트 처리
- [ ] 추가 전략 (MACD, RSI 등)
- [ ] 모니터링 및 알림
- [ ] 성능 최적화

## 라이선스

MIT

