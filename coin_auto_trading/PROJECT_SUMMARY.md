# coin_auto_trading 프로젝트 정리

## 📁 현재 구조

```
coin_auto_trading/
├── app/                    # ✅ 완전히 구현된 코인 자동매매 시스템
│   ├── core/              # 상태 머신, DB, 로거 (구현됨)
│   ├── data/              # 캔들 데이터 모델 (구현됨)
│   ├── features/          # 기술적 지표 (SMA, MACD, RSI 구현됨)
│   ├── strategies/        # 전략 (SMA 전략 구현됨)
│   ├── decision/          # DecisionEngine (구현됨)
│   ├── execution/         # 주문 실행, 중복 방지 (구현됨)
│   ├── backtest/          # 백테스트 엔진 (구현됨)
│   ├── api/               # Mock API (구현됨)
│   └── ops/               # 운영 모듈 (빈 폴더)
├── quantbot/              # ⚠️ 새로 만든 빈 구조 (Sprint 1 뼈대만)
│   └── app/               # FastAPI 구조만 있음 (기능 미구현)
├── cli.py                 # ✅ CLI 도구 (백테스트, 라이브 실행 가능)
├── tests/                 # ✅ 테스트 코드 (상태 머신, 지표 테스트)
├── db/                    # SQLite DB 저장소
├── logs/                  # 로그 파일 저장소
├── requirements.txt       # 의존성 목록
├── verify.sh              # 검증 스크립트 (WSL용)
└── README.md              # 프로젝트 문서
```

## 🎯 두 가지 프로젝트

### 1. `coin_auto_trading/` (완전 구현체) ✅
**상태**: 기능 구현 완료, 실행 가능

**구현된 기능**:
- ✅ 상태 머신 (FLAT/LONG/PENDING)
- ✅ DecisionEngine (백테스트/라이브 공통)
- ✅ 백테스트 엔진
- ✅ SMA 전략
- ✅ 기술적 지표 (SMA, EMA, MACD, RSI)
- ✅ Mock API (Paper Trading)
- ✅ 주문 실행 및 중복 방지
- ✅ SQLite DB 기록
- ✅ CLI 도구

**실행 방법 (WSL + quent_env)**:
```bash
# WSL 진입
wsl

# 프로젝트 폴더로 이동
cd /mnt/c/Users/surro/Documents/01_test/coin_auto_trading

# 가상환경 활성화 (경로 확인 필요)
source quent_env/bin/activate  # 또는 ../quent_env/bin/activate

# 검증 스크립트 실행
bash verify.sh

# 또는 직접 실행
python cli.py backtest --strategy sma --symbol KRW-BTC --timeframe 15m --days 7
```

### 2. `coin_auto_trading/quantbot/` (새 구조) ⚠️
**상태**: 구조만 생성, 기능 미구현

**현재 상태**:
- ✅ 폴더 구조 생성
- ✅ FastAPI 기본 구조
- ✅ `python -m app.api.main` 실행 가능 (기본 엔드포인트만)
- ❌ 실제 트레이딩 기능 없음
- ❌ 24시간 루프 없음

**목적**: Sprint 1의 "뼈대 + 페이퍼로 24h 루프"를 만들기 위한 새 프로젝트

## 🔍 검증 방법 (WSL + quent_env)

### 빠른 검증

```bash
# WSL에서 실행
wsl

# 검증 스크립트 실행
cd /mnt/c/Users/surro/Documents/01_test/coin_auto_trading
bash verify.sh
```

### 수동 검증

```bash
# 1. WSL 진입 및 가상환경 활성화
wsl
cd /mnt/c/Users/surro/Documents/01_test/coin_auto_trading
source quent_env/bin/activate  # 경로 확인 필요

# 2. CLI 도구 확인
python cli.py --help

# 3. 상태 머신 테스트
python -c "from app.core.state_machine import StateMachine, PositionState; sm = StateMachine(); print('초기 상태:', sm.get_state().value)"

# 4. 백테스트 실행
python cli.py backtest --strategy sma --symbol KRW-BTC --timeframe 15m --days 7

# 5. 테스트 실행
pytest tests/ -v
```

## 💡 추천 사항

1. **coin_auto_trading 사용**: 이미 완전히 구현되어 있으므로 바로 사용 가능
2. **quantbot 개발**: 새 구조로 24시간 루프를 구현하려면 기능 추가 필요

## 🚀 빠른 시작

```bash
# WSL에서
wsl
cd /mnt/c/Users/surro/Documents/01_test/coin_auto_trading

# 가상환경 활성화 (경로는 실제 위치에 맞게 수정)
source quent_env/bin/activate  # 또는 ../quent_env/bin/activate

# 의존성 확인
pip list | grep -E "(numpy|pandas|pytest)"

# 백테스트 실행
python cli.py backtest --strategy sma --symbol KRW-BTC --timeframe 15m --days 7 --db

# 결과 확인
python cli.py check-db
```

## 📝 가상환경 경로 확인

가상환경이 다른 위치에 있을 수 있습니다:
- `coin_auto_trading/quent_env/`
- `../quent_env/` (상위 폴더)
- 다른 경로

경로 확인:
```bash
find /mnt/c/Users/surro/Documents/01_test -name "quent_env" -type d
```
