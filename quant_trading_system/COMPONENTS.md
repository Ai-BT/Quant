# 컴포넌트 상세 설명

## 1. Backend Components

### 1.1 API Layer (FastAPI)

#### 1.1.1 Strategy API (`api/v1/strategies.py`)
**역할**: 전략 관리 API

**엔드포인트**:
- `GET /api/v1/strategies` - 전략 목록 조회
- `GET /api/v1/strategies/{id}` - 전략 상세 조회
- `POST /api/v1/strategies` - 새 전략 생성
- `PUT /api/v1/strategies/{id}` - 전략 수정
- `DELETE /api/v1/strategies/{id}` - 전략 삭제
- `POST /api/v1/strategies/{id}/start` - 전략 시작
- `POST /api/v1/strategies/{id}/stop` - 전략 중지
- `POST /api/v1/strategies/{id}/backtest` - 백테스트 실행

**책임**:
- 전략 CRUD 작업
- 전략 실행 제어
- 백테스트 요청 처리

#### 1.1.2 Order API (`api/v1/orders.py`)
**역할**: 주문 관리 API

**엔드포인트**:
- `GET /api/v1/orders` - 주문 목록 조회
- `GET /api/v1/orders/{id}` - 주문 상세 조회
- `POST /api/v1/orders/{id}/cancel` - 주문 취소
- `GET /api/v1/balances` - 잔고 조회
- `GET /api/v1/trades` - 거래 내역 조회

**책임**:
- 주문 조회 및 취소
- 잔고 및 거래 내역 조회

#### 1.1.3 Monitoring API (`api/v1/monitoring.py`)
**역할**: 모니터링 및 알림 API

**엔드포인트**:
- `GET /api/v1/status` - 시스템 상태
- `GET /api/v1/metrics` - 성능 메트릭
- `GET /api/v1/logs` - 로그 조회
- `GET /api/v1/alerts` - 알림 조회

**책임**:
- 시스템 상태 모니터링
- 로그 및 알림 관리

#### 1.1.4 ML Model API (`api/v1/ml_models.py`)
**역할**: AI 모델 관리 API

**엔드포인트**:
- `GET /api/v1/ml-models` - 모델 목록 조회
- `GET /api/v1/ml-models/{id}` - 모델 상세 조회
- `POST /api/v1/ml-models` - 새 모델 등록
- `PUT /api/v1/ml-models/{id}` - 모델 업데이트
- `DELETE /api/v1/ml-models/{id}` - 모델 삭제
- `POST /api/v1/ml-models/{id}/train` - 모델 학습 요청
- `GET /api/v1/ml-models/{id}/training-status` - 학습 상태 조회
- `POST /api/v1/ml-models/{id}/predict` - 추론 요청
- `GET /api/v1/ml-models/{id}/metrics` - 모델 성능 조회
- `POST /api/v1/ml-models/{id}/deploy` - 모델 배포/활성화

**책임**:
- 모델 CRUD 작업
- 모델 학습 요청 관리
- 모델 추론 요청 처리
- 모델 버전 관리

### 1.1.5 WebSocket (`api/websocket/connections.py`)
**역할**: 실시간 통신

**연결**:
- `/ws` - 실시간 이벤트 스트림

**이벤트 타입**:
- `strategy.signal` - 전략 신호 발생
- `order.executed` - 주문 실행 완료
- `order.failed` - 주문 실패
- `system.alert` - 시스템 알림

**책임**:
- WebSocket 연결 관리
- Redis Pub/Sub 구독
- 클라이언트에 실시간 이벤트 전송

### 1.2 Service Layer

#### 1.2.1 Strategy Service (`services/strategy_service.py`)
**역할**: 전략 비즈니스 로직

**기능**:
- 전략 생성/수정/삭제
- 전략 실행 상태 관리
- 전략 설정 검증
- 백테스트 실행 및 결과 저장
- 전략 성과 계산

**의존성**:
- DB (전략 저장)
- Redis (실행 상태)
- Strategy Engine Worker (실행 요청)

#### 1.2.2 Order Service (`services/order_service.py`)
**역할**: 주문 비즈니스 로직

**기능**:
- 주문 내역 조회 및 필터링
- 주문 취소 요청 처리
- 잔고 조회 및 계산
- 거래 내역 집계

**의존성**:
- DB (주문 내역)
- UpbitAdapter (실제 API 호출)

#### 1.2.3 ML Model Service (`services/ml_model_service.py`)
**역할**: ML 모델 비즈니스 로직

**기능**:
- 모델 등록 및 메타데이터 관리
- 모델 학습 작업 관리
- 모델 추론 요청 처리
- 모델 성능 평가 및 비교
- 모델 버전 관리
- A/B 테스트 관리

**의존성**:
- DB (모델 메타데이터)
- ML Model Service Worker (실제 학습/추론)
- Model Storage (모델 파일)

#### 1.2.4 Monitoring Service (`services/monitoring_service.py`)
**역할**: 모니터링 비즈니스 로직

**기능**:
- 시스템 상태 수집
- 성능 메트릭 계산
- 로그 관리
- 알림 생성 및 전송

**의존성**:
- Redis (상태 정보)
- DB (로그 저장)

### 1.3 Worker Layer

#### 1.3.1 Strategy Engine Worker (`workers/strategy_engine/`)
**역할**: 전략 로직 실행

**구성 요소**:
- `main.py`: 워커 진입점 및 메인 루프
- `engine.py`: 전략 엔진 코어 로직
- `data_fetcher.py`: 시장 데이터 수집
- `signal_generator.py`: 매수/매도 신호 생성

**동작 흐름**:
1. Redis에서 실행 중인 전략 목록 조회
2. 각 전략별로 시장 데이터 수집
3. 전략 타입에 따라 분기:
   - **전통 전략**: 기술적 지표 계산 및 신호 생성
   - **AI 전략**: ML Model Service에 추론 요청 → 결과 기반 신호 생성
   - **하이브리드 전략**: 전통 전략 + AI 전략 결과 조합
4. 신호 발생 시 Redis 큐에 전송
5. 전략 상태 업데이트

**특징**:
- 전략 로직만 담당 (주문 실행 X)
- 전통 전략과 AI 전략 모두 지원
- 순수한 비즈니스 로직
- 백테스트와 동일한 로직 사용 가능
- ML Model Service와 통신하여 AI 추론 결과 활용

#### 1.3.2 ML Model Service Worker (`workers/ml_model_service/`)
**역할**: ML 모델 학습 및 추론

**구성 요소**:
- `main.py`: 워커 진입점 및 메인 루프
- `trainer.py`: 모델 학습 로직
- `inference_service.py`: 모델 추론 서비스
- `model_manager.py`: 모델 관리 (로드, 저장, 버전 관리)
- `feature_engineering.py`: 특성 엔지니어링

**학습 워크플로우**:
1. Redis 큐에서 학습 작업 수신
2. 과거 시장 데이터 수집
3. 특성 엔지니어링 및 전처리
4. 모델 학습 실행
5. 모델 평가 및 검증
6. 모델 저장 및 버전 관리
7. 학습 결과 DB 저장
8. Redis 이벤트 버스에 완료 알림 전송

**추론 워크플로우**:
1. Strategy Engine으로부터 추론 요청 수신
2. 요청된 모델 로드 (캐시 또는 디스크)
3. 입력 데이터 전처리
4. 모델 추론 실행
5. 결과 반환

**특징**:
- 학습과 추론을 독립적으로 처리
- 모델 캐싱으로 추론 속도 최적화
- GPU 지원 (선택사항)

#### 1.3.3 Order Executor Worker (`workers/order_executor/`)
**역할**: 실제 주문 실행

**구성 요소**:
- `main.py`: 워커 진입점 및 메인 루프
- `executor.py`: 주문 실행 로직
- `risk_manager.py`: 리스크 관리
- `order_validator.py`: 주문 검증

**동작 흐름**:
1. Redis 큐에서 주문 신호 수신
2. 리스크 관리 검증 (최대 손실, 포지션 크기 등)
3. 주문 검증 (잔고, 최소 주문 금액 등)
4. UpbitAdapter를 통한 실제 주문 실행
5. 주문 결과 DB 저장
6. Redis 이벤트 버스에 결과 전송

**특징**:
- 실제 주문 실행만 담당
- 리스크 관리 및 검증 포함
- 실패 시 재시도 로직

### 1.4 Strategy Library (`strategies/`)

#### 1.4.1 Base Strategy (`strategies/base.py`)
**역할**: 모든 전략의 기본 클래스

**인터페이스**:
```python
class BaseStrategy:
    def initialize(self, config: dict)
    def on_data(self, data: MarketData) -> Signal
    def on_signal(self, signal: Signal)
    def get_state(self) -> dict
```

**책임**:
- 공통 전략 인터페이스 제공
- 공통 유틸리티 메서드
- 상태 관리

#### 1.4.2 Traditional Strategy Implementations
전통 전략은 `BaseStrategy`를 상속받아 구현:
- `traditional/sma_crossover/`: SMA 크로스오버 전략
- `traditional/macd/`: MACD 전략
- `traditional/rsi/`: RSI 전략

**특징**:
- 독립적인 모듈
- 설정 파일 분리
- 테스트 가능
- 기술적 지표 기반

#### 1.4.3 AI Strategy Implementations
AI 전략은 `BaseAIStrategy`를 상속받아 구현:
- `ai/lstm_predictor/`: LSTM 기반 예측 전략
- `ai/transformer/`: Transformer 기반 전략
- `ai/xgboost_classifier/`: XGBoost 분류 전략
- `ai/ensemble/`: 앙상블 전략

**특징**:
- ML 모델 추론 결과 활용
- 모델 ID로 특정 모델 참조
- 추론 실패 시 폴백 메커니즘
- 전통 전략과 조합 가능

### 1.5 Adapter Layer (`adapters/`)

#### 1.5.1 UpbitAdapter (`adapters/upbit/adapter.py`)
**역할**: Upbit API 어댑터

**기능**:
- 주문 (매수/매도)
- 주문 취소
- 잔고 조회
- OHLCV 데이터 조회
- Rate Limit 관리
- 에러 처리

**특징**:
- 외부 API와의 추상화 계층
- 다른 거래소 추가 시 인터페이스 유지

## 2. Frontend Components

### 2.1 Dashboard Component
**역할**: 메인 대시보드

**기능**:
- 전체 시스템 상태 표시
- 실시간 수익률 차트
- 활성 전략 목록
- 최근 주문 내역

### 2.2 Strategy Management Component
**역할**: 전략 관리

**기능**:
- 전략 목록 조회
- 전략 생성/수정/삭제
- 전략 시작/중지
- 백테스트 실행 및 결과 확인

### 2.3 Order History Component
**역할**: 주문 내역 조회

**기능**:
- 주문 목록 조회 및 필터링
- 주문 상세 정보
- 주문 취소
- 거래 내역 차트

### 2.4 Real-time Monitor Component
**역할**: 실시간 모니터링

**기능**:
- WebSocket 연결
- 실시간 이벤트 수신 및 표시
- 알림 표시
- 로그 스트림

## 3. Infrastructure Components

### 3.1 Database (PostgreSQL)
**역할**: 영구 데이터 저장

**테이블**:
- `users`: 사용자 정보
- `strategies`: 전략 설정
- `orders`: 주문 내역
- `trades`: 거래 내역
- `backtests`: 백테스트 결과
- `logs`: 시스템 로그

### 3.2 Redis
**역할**: 캐시 및 메시지 큐

**사용 용도**:
- 시장 데이터 캐시
- 세션 관리
- 메시지 큐 (전략 신호, 주문 요청)
- Pub/Sub (실시간 이벤트)
- Rate Limit 관리

### 3.3 Model Storage
**역할**: 학습된 모델 파일 저장

**저장 방식**:
- 파일 시스템 (로컬 또는 NFS)
- 객체 스토리지 (S3, MinIO 등)
- MLflow Artifact Store

**저장 내용**:
- 모델 가중치 파일 (.pkl, .h5, .pt 등)
- 모델 아키텍처 정의
- 전처리 파이프라인
- 특성 목록 및 메타데이터

### 3.4 Docker
**역할**: 컨테이너화 및 배포

**컨테이너**:
- `backend`: FastAPI 서버
- `frontend`: React/Vue 앱
- `strategy_worker`: 전략 엔진 워커
- `order_worker`: 주문 실행 워커
- `ml_model_worker`: ML 모델 서비스 워커
- `postgres`: 데이터베이스
- `redis`: Redis 서버
- `nginx`: 리버스 프록시
- `mlflow` (선택사항): ML 모델 관리 플랫폼

## 4. 데이터 흐름 상세

### 4.1 전통 전략 실행 흐름
```
User (Frontend)
  ↓ POST /api/v1/strategies/{id}/start
API Gateway
  ↓
Strategy Service
  ↓ DB 업데이트 (상태: running)
  ↓ Redis 큐 (strategy.start)
Strategy Engine Worker
  ↓ 시장 데이터 수집
  ↓ 전략 로직 실행
  ↓ 신호 발생
  ↓ Redis 큐 (order.signal)
Order Executor Worker
  ↓ 리스크 검증
  ↓ UpbitAdapter 호출
  ↓ 주문 실행
  ↓ DB 저장
  ↓ Redis Pub/Sub (order.executed)
WebSocket
  ↓
Frontend (실시간 업데이트)
```

### 4.2 실시간 모니터링 흐름
```
Strategy Engine / Order Executor
  ↓ 이벤트 발생
  ↓ Redis Pub/Sub
API Gateway (WebSocket)
  ↓
Frontend (WebSocket 클라이언트)
  ↓ UI 업데이트
```

## 5. 핵심 설계 원칙

### 5.1 관심사의 분리 (Separation of Concerns)
- **전략 로직**: Strategy Engine만 담당
- **주문 실행**: Order Executor만 담당
- **API**: FastAPI만 담당
- **UI**: Frontend만 담당

### 5.2 단일 책임 원칙 (Single Responsibility)
- 각 컴포넌트는 하나의 책임만 가짐
- 변경 시 다른 컴포넌트에 영향 최소화

### 5.3 의존성 역전 (Dependency Inversion)
- 고수준 모듈이 저수준 모듈에 의존하지 않음
- 인터페이스를 통한 추상화

### 5.4 확장성 (Scalability)
- Worker 수평 확장 가능
- Redis를 통한 분산 처리
- 마이크로서비스 아키텍처

### 5.5 안정성 (Reliability)
- 무중단 운영 (자동 재시작)
- 에러 처리 및 재시도 로직
- 모니터링 및 알림

