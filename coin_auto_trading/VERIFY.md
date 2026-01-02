# 검증 가이드 (WSL + quant_env)

## ✅ 검증 완료 항목

### 1. 환경 설정
- [x] WSL 접근 가능
- [x] 가상환경 위치: `../quant_env` (상위 폴더)
- [x] Python 버전: 3.8.10
- [x] CLI 도구 정상 작동

### 2. 모듈 검증
- [x] 상태 머신 (StateMachine) import 성공
- [x] 기술적 지표 (SMA) 계산 성공
- [x] CLI 도구 실행 가능

## 🚀 실행 명령어

### 기본 검증

```bash
# WSL 진입
wsl

# 프로젝트 폴더로 이동
cd /mnt/c/Users/surro/Documents/01_test/coin_auto_trading

# 가상환경 활성화
source ../quant_env/bin/activate

# 검증 스크립트 실행
bash verify.sh
```

### 수동 검증

```bash
# 1. 상태 머신 테스트
python -c "from app.core.state_machine import StateMachine, PositionState; sm = StateMachine(); print('초기 상태:', sm.get_state().value)"

# 2. 기술적 지표 테스트
python -c "from app.features.indicators import sma; result = sma([100, 102, 104, 103, 105], 5); print('SMA 결과:', result[-1])"

# 3. 백테스트 실행 (7일)
python cli.py backtest --strategy sma --symbol KRW-BTC --timeframe 15m --days 7

# 4. DB 상태 확인
python cli.py check-db

# 5. 테스트 실행
pytest tests/ -v
```

## 📊 프로젝트 요약

### coin_auto_trading/ (완전 구현체) ✅

**구현된 기능**:
- 상태 머신 (FLAT/LONG/PENDING)
- DecisionEngine
- 백테스트 엔진
- SMA 전략
- 기술적 지표 (SMA, EMA, MACD, RSI)
- Mock API
- 주문 실행 및 중복 방지
- SQLite DB 기록
- CLI 도구

**실행 가능한 명령어**:
```bash
# 백테스트
python cli.py backtest --strategy sma --symbol KRW-BTC --timeframe 15m --days 7

# DB 확인
python cli.py check-db

# 라이브 트레이딩 (Paper Trading)
python cli.py live --strategy sma --symbol KRW-BTC
```

### quantbot/ (새 구조) ⚠️

- 폴더 구조만 생성됨
- FastAPI 기본 구조만 있음
- 실제 기능은 미구현

## 🔧 문제 해결

### 가상환경을 찾을 수 없을 때

```bash
# 가상환경 위치 확인
find /mnt/c/Users/surro/Documents/01_test -name "*env" -type d

# 현재 위치 확인
pwd
# /mnt/c/Users/surro/Documents/01_test/coin_auto_trading 이어야 함
```

### 모듈을 찾을 수 없을 때

```bash
# Python 경로 확인
python -c "import sys; print('\n'.join(sys.path))"

# 현재 디렉토리 확인
ls -la app/
```

### 의존성 설치

```bash
source ../quant_env/bin/activate
pip install -r requirements.txt
```

