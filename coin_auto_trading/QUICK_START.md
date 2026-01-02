# 빠른 시작 가이드 (WSL + quent_env)

## 환경 설정

```bash
# WSL 진입
wsl

# 프로젝트 폴더로 이동
cd /mnt/c/Users/surro/Documents/01_test/coin_auto_trading

# 가상환경 활성화
source quent_env/bin/activate

# 의존성 확인
pip list | grep -E "(numpy|pandas|pytest)"
```

## 검증 명령어

### 1. 기본 검증

```bash
# CLI 도구 확인
python cli.py --help

# 상태 머신 테스트
python -c "from app.core.state_machine import StateMachine, PositionState; sm = StateMachine(); print('초기 상태:', sm.get_state().value)"

# 기술적 지표 테스트
python -c "from app.features.indicators import sma; result = sma([100, 102, 104, 103, 105], 3); print('SMA 결과:', result)"
```

### 2. 백테스트 실행

```bash
# 기본 백테스트 (7일)
python cli.py backtest --strategy sma --symbol KRW-BTC --timeframe 15m --days 7

# 상세 옵션
python cli.py backtest \
  --strategy sma \
  --symbol KRW-BTC \
  --timeframe 15m \
  --fast-period 5 \
  --slow-period 20 \
  --slow-period 20 \
  --initial-cash 1000000 \
  --days 30 \
  --db  # DB에 기록
```

### 3. DB 상태 확인

```bash
python cli.py check-db
```

### 4. 테스트 실행

```bash
# 모든 테스트
pytest tests/

# 특정 테스트
pytest tests/test_state_machine.py -v
pytest tests/test_indicators.py -v
```

## 프로젝트 구조 요약

### ✅ 완전히 구현된 모듈 (coin_auto_trading/)

- **app/core/**: 상태 머신, DB, 로거
- **app/data/**: 캔들 데이터 모델
- **app/features/**: 기술적 지표 (SMA, EMA, MACD, RSI)
- **app/strategies/**: SMA 전략
- **app/decision/**: DecisionEngine
- **app/execution/**: 주문 실행, 중복 방지
- **app/backtest/**: 백테스트 엔진
- **app/api/**: Mock API
- **cli.py**: CLI 도구

### ⚠️ 새 구조 (quantbot/)

- 폴더 구조만 생성됨
- FastAPI 기본 구조만 있음
- 실제 기능은 미구현

## 문제 해결

### 모듈을 찾을 수 없을 때

```bash
# 현재 디렉토리 확인
pwd
# /mnt/c/Users/surro/Documents/01_test/coin_auto_trading 이어야 함

# Python 경로 확인
python -c "import sys; print('\n'.join(sys.path))"
```

### 의존성 설치

```bash
source quent_env/bin/activate
pip install -r requirements.txt
```

