# Sprint 1 체크리스트 - "뼈대 + 페이퍼로 24h 루프"

## ✅ 완료된 작업

### 1. 프로젝트 구조 생성
- [x] `quantbot/` 루트 폴더 생성 (`coin_auto_trading/quantbot/`)
- [x] `app/` 메인 애플리케이션 폴더 생성
- [x] `app/core/` - 핵심 모듈
- [x] `app/data/` - 데이터 모듈
- [x] `app/features/` - 피처 모듈
- [x] `app/strategies/` - 전략 모듈
- [x] `app/decision/` - 결정 엔진 모듈
- [x] `app/execution/` - 실행 모듈
- [x] `app/backtest/` - 백테스트 모듈
- [x] `app/api/` - API 모듈
- [x] `app/ops/` - 운영 모듈
- [x] `tests/` - 테스트 폴더

### 2. 패키징 파일
- [x] `pyproject.toml` 생성 (Python 3.11 기준)
- [x] `requirements.txt` 생성
- [x] 모든 모듈에 `__init__.py` 파일 생성

### 3. 실행 가능한 구조
- [x] `app/__main__.py` 생성 (`python -m app` 실행 가능)
- [x] `app/api/main.py` 생성 (`python -m app.api.main` 실행 가능)
- [x] FastAPI 기본 구조 구현

### 4. 문서화
- [x] `README.md` 작성
  - [x] 프로젝트 구조 설명
  - [x] 설치 방법
  - [x] 실행 방법
  - [x] **페이퍼 모드 실행 방법** (상세 설명 포함)
- [x] `.env.example` 생성
- [x] `.gitignore` 생성

### 5. 의존성
- [x] 필수 의존성: fastapi, uvicorn, pydantic, numpy, pandas
- [x] 선택 의존성: ta, httpx, apscheduler, sqlalchemy
- [x] 테스트 의존성: pytest

## 🔄 다음 단계 (Sprint 1 계속)

### 핵심 모듈 구현
- [ ] 상태 머신 구현 (`app/core/state_machine.py`)
- [ ] 데이터베이스 모델 구현 (`app/core/database.py`)
- [ ] 로거 구현 (`app/core/logger.py`)

### 데이터 모듈
- [ ] 캔들 데이터 모델 (`app/data/candle.py`)
- [ ] 데이터 수집기 (`app/data/collector.py`)

### 피처 모듈
- [ ] 기술적 지표 계산 (`app/features/indicators.py`)

### 전략 모듈
- [ ] 전략 베이스 클래스 (`app/strategies/base_strategy.py`)
- [ ] SMA 전략 예제 (`app/strategies/sma_strategy.py`)

### 결정 엔진
- [ ] DecisionEngine 구현 (`app/decision/engine.py`)

### 실행 모듈
- [ ] OrderExecutor 구현 (`app/execution/executor.py`)
- [ ] Mock API 구현 (`app/api/mock_api.py`)

### 백테스트
- [ ] BacktestEngine 구현 (`app/backtest/engine.py`)

### API 확장
- [ ] 트레이딩 엔드포인트 추가
- [ ] 상태 조회 엔드포인트 추가

### **24시간 루프 (핵심)**
- [ ] 스케줄러 설정 (`app/ops/scheduler.py`)
- [ ] 캔들 마감 이벤트 처리
- [ ] 페이퍼 모드 루프 구현
- [ ] APScheduler를 사용한 24시간 자동 실행

## 📝 참고사항

### 실행 방법 확인
1. `cd coin_auto_trading/quantbot`
2. `python -m app` 실행 테스트
3. `python -m app.api.main` 실행 테스트 (의존성 설치 후)

### 환경 설정
1. 가상환경 생성: `python -m venv venv`
2. 가상환경 활성화: `venv\Scripts\activate` (Windows)
3. 의존성 설치: `pip install -r requirements.txt`
4. 환경 변수 설정: `.env.example`을 복사하여 `.env` 생성

### Python 버전
- Python 3.11 이상 필요
- `pyproject.toml`에 `requires-python = ">=3.11"` 명시

### 다음 단계 우선순위
1. **24시간 루프 구현** (Sprint 1 핵심 목표)
2. 상태 머신 및 DecisionEngine
3. 페이퍼 모드 Mock API
4. 기본 전략 구현

