# Backend API

FastAPI 기반 퀀트 트레이딩 시스템 백엔드

## 설치

```bash
cd backend
pip install -r requirements.txt
```

## 환경 변수 설정

`.env.example` 파일을 복사하여 `.env` 파일을 생성하고 값을 수정하세요:

```bash
cp .env.example .env
```

## 실행

```bash
# 방법 1: 직접 실행
python -m app.main

# 방법 2: uvicorn 사용
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

서버가 실행되면 다음 URL에서 접근할 수 있습니다:
- API 문서: http://localhost:8000/docs
- 대체 문서: http://localhost:8000/redoc
- Health check: http://localhost:8000/api/v1/health

## API 엔드포인트

### 서버 상태 확인
- `GET /api/v1/health` - 서버 상태 확인

### 전략 관리
- `GET /api/v1/strategies` - 전략 목록 조회
- `GET /api/v1/strategies/{strategy_id}` - 전략 상세 조회
- `POST /api/v1/strategies/{strategy_id}/start` - 전략 시작
- `POST /api/v1/strategies/{strategy_id}/stop` - 전략 중지

### 포지션 조회
- `GET /api/v1/positions` - 현재 포지션 목록 조회
- `GET /api/v1/positions/{market}` - 특정 마켓 포지션 조회

### 거래 내역 조회
- `GET /api/v1/trades` - 최근 거래 내역 조회
  - Query Parameters:
    - `limit`: 조회할 개수 (기본값: 20, 최대: 100)
    - `offset`: 시작 위치 (기본값: 0)
- `GET /api/v1/trades/{trade_id}` - 특정 거래 내역 조회

### 로그 조회
- `GET /api/v1/logs` - 로그 조회
  - Query Parameters:
    - `level`: 로그 레벨 (INFO, WARNING, ERROR, DEBUG)
    - `type`: 로그 타입 (strategy, order, system)
    - `limit`: 조회할 개수 (기본값: 50, 최대: 200)
    - `offset`: 시작 위치 (기본값: 0)

## Mock 데이터

현재는 Mock 데이터를 사용합니다. 실제 거래소 연결은 추후 구현 예정입니다.

Mock 데이터에는 다음이 포함됩니다:
- 2개의 전략 (SMA 크로스오버, LSTM 예측)
- 2개의 포지션 (KRW-BTC, KRW-ETH)
- 20개의 거래 내역
- 50개의 로그



