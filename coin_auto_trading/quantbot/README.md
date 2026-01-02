# QuantBot - 24시간 코인 자동매매 시스템

Python 3.11 기반의 코인 자동매매 시스템입니다.

## 프로젝트 구조

```
quantbot/
├── app/
│   ├── __init__.py
│   ├── __main__.py          # python -m app 실행 시 호출
│   ├── core/                # 핵심 모듈 (상태 머신, DB, 로거)
│   ├── data/                # 캔들 데이터 관리
│   ├── features/            # 기술적 지표 (SMA, MACD, RSI 등)
│   ├── strategies/          # 트레이딩 전략
│   ├── decision/            # 결정 엔진 (백테스트/라이브 공통)
│   ├── execution/           # 주문 실행, 중복 방지
│   ├── backtest/            # 백테스트 엔진
│   ├── api/                 # FastAPI REST API
│   │   └── main.py          # python -m app.api.main 실행 시 호출
│   └── ops/                 # 모니터링, 알림
├── tests/                   # 테스트 코드
├── pyproject.toml           # 프로젝트 설정
├── requirements.txt          # 의존성 목록
└── README.md
```

## 설치

### 1. 가상환경 생성 및 활성화

```bash
# Python 3.11 이상 필요
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. 의존성 설치

```bash
# requirements.txt 사용
pip install -r requirements.txt

# 또는 pyproject.toml 사용
pip install -e .
```

### 3. 환경 변수 설정

```bash
# .env.example을 복사하여 .env 파일 생성
cp .env.example .env

# .env 파일 수정 (API 키 등)
```

## 실행 방법

### 1. 기본 실행

```bash
# quantbot 폴더로 이동
cd quantbot

# 애플리케이션 정보 확인
python -m app
```

### 2. API 서버 실행

```bash
# quantbot 폴더에서 실행
cd quantbot
python -m app.api.main

# 또는 uvicorn 직접 사용
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
```

서버 실행 후:
- API 문서: http://localhost:8000/docs
- 헬스 체크: http://localhost:8000/health

### 3. 페이퍼 모드 실행 (Paper Trading)

페이퍼 모드는 실제 자금 없이 가상의 거래를 시뮬레이션하는 모드입니다.

```bash
# .env 파일에서 TRADING_MODE=paper 설정

# API 서버 실행
cd quantbot
python -m app.api.main

# 또는 향후 구현될 CLI 도구 사용
# python -m app.cli paper --strategy sma --symbol KRW-BTC
```

**페이퍼 모드 특징:**
- 실제 자금 사용 안 함
- Mock API를 사용하여 거래 시뮬레이션
- 모든 거래 내역이 DB에 기록됨
- 백테스트와 동일한 DecisionEngine 사용
- 24시간 자동 루프 실행 (향후 구현)

**페이퍼 모드 실행 예시:**
```bash
# 1. 환경 변수 설정
export TRADING_MODE=paper
export DEFAULT_SYMBOL=KRW-BTC
export INITIAL_BALANCE=1000000

# 2. API 서버 시작
python -m app.api.main

# 3. 트레이딩 루프 시작 (향후 구현)
# 자동으로 캔들 마감 이벤트를 감지하고 거래 결정 수행
```

### 4. 라이브 모드 실행 (실거래)

⚠️ **주의**: 실거래 모드는 실제 자금을 사용합니다. 충분한 테스트 후 사용하세요.

```bash
# .env 파일 설정
# TRADING_MODE=live
# UPBIT_ACCESS_KEY=your_access_key
# UPBIT_SECRET_KEY=your_secret_key

# API 서버 실행
cd quantbot
python -m app.api.main
```

## 개발

### 테스트 실행

```bash
cd quantbot
pytest

# 커버리지 포함
pytest --cov=app

# 특정 테스트만 실행
pytest tests/test_core.py
```

### 코드 포맷팅

```bash
# black 사용 (설치 필요: pip install black)
black app/ tests/

# flake8 사용 (설치 필요: pip install flake8)
flake8 app/ tests/
```

## 핵심 원칙

- **백테스트와 라이브가 동일한 DecisionEngine 사용**
- **상태 머신 명확한 구현** (FLAT/LONG/PENDING)
- **멀티 타임프레임 지원**, 판단은 캔들 마감 이벤트에서만
- **모든 결정 DB 기록** (시그널/피처/액션/포지션/주문)
- **중복 주문 방지** (idempotency)
- **안정성/재현성/로그 우선**

## 의존성

### 필수
- `fastapi`: REST API 프레임워크
- `uvicorn`: ASGI 서버
- `pydantic`: 데이터 검증
- `numpy`: 수치 계산
- `pandas`: 데이터 처리

### 선택
- `ta`: 기술적 지표 계산
- `httpx`: HTTP 클라이언트
- `apscheduler`: 스케줄링
- `sqlalchemy`: ORM

### 테스트
- `pytest`: 테스트 프레임워크

## 라이선스

MIT

