# 디렉토리 구조 설계

## 전체 구조

```
quant_trading_system/
│
├── backend/                          # Backend 서버
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI 앱 진입점
│   │   │
│   │   ├── api/                      # API 라우터
│   │   │   ├── __init__.py
│   │   │   ├── deps.py               # 의존성 (인증, DB 등)
│   │   │   │
│   │   │   ├── v1/                   # API v1
│   │   │   │   ├── __init__.py
│   │   │   │   ├── strategies.py     # 전략 API
│   │   │   │   ├── orders.py         # 주문 API
│   │   │   │   ├── monitoring.py     # 모니터링 API
│   │   │   │   ├── ml_models.py      # ML 모델 API
│   │   │   │   └── auth.py          # 인증 API
│   │   │   │
│   │   │   └── websocket/            # WebSocket
│   │   │       ├── __init__.py
│   │   │       └── connections.py    # WebSocket 연결 관리
│   │   │
│   │   ├── core/                     # 핵심 설정 및 유틸리티
│   │   │   ├── __init__.py
│   │   │   ├── config.py             # 설정 관리
│   │   │   ├── database.py           # DB 연결
│   │   │   ├── redis.py               # Redis 연결
│   │   │   ├── security.py            # 인증/인가
│   │   │   └── logging.py            # 로깅 설정
│   │   │
│   │   ├── models/                   # SQLAlchemy 모델
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # 기본 모델
│   │   │   ├── user.py                # 사용자 모델
│   │   │   ├── strategy.py            # 전략 모델
│   │   │   ├── order.py               # 주문 모델
│   │   │   ├── trade.py               # 거래 내역 모델
│   │   │   └── ml_model.py            # ML 모델 메타데이터 모델
│   │   │
│   │   ├── schemas/                   # Pydantic 스키마
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── strategy.py
│   │   │   ├── order.py
│   │   │   └── trade.py
│   │   │
│   │   ├── services/                  # 비즈니스 로직
│   │   │   ├── __init__.py
│   │   │   ├── strategy_service.py    # 전략 서비스
│   │   │   ├── order_service.py       # 주문 서비스
│   │   │   ├── monitoring_service.py  # 모니터링 서비스
│   │   │   └── ml_model_service.py    # ML 모델 서비스
│   │   │
│   │   ├── adapters/                  # 외부 API 어댑터
│   │   │   ├── __init__.py
│   │   │   └── upbit/
│   │   │       ├── __init__.py
│   │   │       ├── adapter.py         # UpbitAdapter
│   │   │       ├── exceptions.py       # 예외 처리
│   │   │       └── rate_limit.py      # Rate Limit 관리
│   │   │
│   │   └── utils/                     # 유틸리티
│   │       ├── __init__.py
│   │       ├── validators.py          # 검증 함수
│   │       └── helpers.py             # 헬퍼 함수
│   │
│   ├── workers/                       # Background Workers
│   │   ├── __init__.py
│   │   │
│   │   ├── strategy_engine/           # 전략 엔진 워커
│   │   │   ├── __init__.py
│   │   │   ├── main.py                # 워커 진입점
│   │   │   ├── engine.py               # 전략 엔진 로직
│   │   │   ├── data_fetcher.py        # 시장 데이터 수집
│   │   │   ├── signal_generator.py    # 신호 생성
│   │   │   └── ai_strategy_handler.py # AI 전략 처리기
│   │   │
│   │   ├── order_executor/            # 주문 실행 워커
│   │   │   ├── __init__.py
│   │   │   ├── main.py                 # 워커 진입점
│   │   │   ├── executor.py             # 주문 실행 로직
│   │   │   ├── risk_manager.py         # 리스크 관리
│   │   │   └── order_validator.py     # 주문 검증
│   │   │
│   │   └── ml_model_service/          # ML 모델 서비스 워커
│   │       ├── __init__.py
│   │       ├── main.py                 # 워커 진입점
│   │       ├── trainer.py              # 모델 학습
│   │       ├── inference_service.py    # 추론 서비스
│   │       ├── model_manager.py        # 모델 관리
│   │       └── feature_engineering.py  # 특성 엔지니어링
│   │
│   ├── strategies/                       # 전략 라이브러리
│   │   ├── __init__.py
│   │   ├── base.py                    # 기본 전략 클래스
│   │   │
│   │   ├── sma_crossover/             # SMA 크로스오버 전략
│   │   │   ├── __init__.py
│   │   │   ├── strategy.py
│   │   │   └── config.py
│   │   │
│   │   ├── macd/                      # MACD 전략
│   │   │   ├── __init__.py
│   │   │   ├── strategy.py
│   │   │   └── config.py
│   │   │
│   │   └── rsi/                       # RSI 전략
│   │       ├── __init__.py
│   │       ├── strategy.py
│   │       └── config.py
│   │
│   ├── tests/                         # 테스트
│   │   ├── __init__.py
│   │   ├── test_api/
│   │   ├── test_services/
│   │   ├── test_workers/
│   │   └── test_strategies/
│   │
│   ├── ml/                            # ML 관련 코드
│   │   ├── __init__.py
│   │   ├── models/                    # ML 모델 정의
│   │   │   ├── __init__.py
│   │   │   ├── lstm_model.py          # LSTM 모델
│   │   │   ├── transformer_model.py   # Transformer 모델
│   │   │   ├── xgboost_model.py       # XGBoost 모델
│   │   │   └── base_model.py          # 기본 모델 클래스
│   │   │
│   │   ├── features/                  # 특성 엔지니어링
│   │   │   ├── __init__.py
│   │   │   ├── technical_indicators.py # 기술적 지표
│   │   │   ├── price_features.py      # 가격 특성
│   │   │   └── volume_features.py     # 거래량 특성
│   │   │
│   │   ├── training/                  # 학습 관련
│   │   │   ├── __init__.py
│   │   │   ├── data_loader.py         # 데이터 로더
│   │   │   ├── trainer.py             # 학습기
│   │   │   └── evaluator.py           # 평가기
│   │   │
│   │   └── inference/                 # 추론 관련
│   │       ├── __init__.py
│   │       ├── predictor.py           # 예측기
│   │       └── model_loader.py        # 모델 로더
│   │
│   ├── models_storage/                # 학습된 모델 저장소
│   │   ├── lstm/
│   │   ├── transformer/
│   │   └── xgboost/
│   │
│   ├── alembic/                       # DB 마이그레이션
│   │   ├── versions/
│   │   └── env.py
│   │
│   ├── requirements.txt
│   ├── requirements-ml.txt            # ML 관련 패키지
│   ├── .env.example
│   └── Dockerfile
│
├── frontend/                          # Frontend (React/Vue)
│   ├── src/
│   │   ├── components/                # 컴포넌트
│   │   │   ├── Dashboard/             # 대시보드
│   │   │   ├── Strategy/              # 전략 관리
│   │   │   ├── Orders/                # 주문 내역
│   │   │   ├── Charts/                # 차트
│   │   │   └── Settings/              # 설정
│   │   │
│   │   ├── services/                  # API 서비스
│   │   │   ├── api.js
│   │   │   ├── websocket.js
│   │   │   └── auth.js
│   │   │
│   │   ├── store/                     # 상태 관리 (Redux/Vuex)
│   │   │   ├── modules/
│   │   │   │   ├── strategy.js
│   │   │   │   ├── order.js
│   │   │   │   └── auth.js
│   │   │   └── index.js
│   │   │
│   │   ├── utils/                     # 유틸리티
│   │   └── App.jsx / App.vue
│   │
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
│
├── docker/                            # Docker 설정
│   ├── docker-compose.yml              # 전체 서비스 오케스트레이션
│   ├── docker-compose.dev.yml         # 개발 환경
│   ├── docker-compose.prod.yml        # 프로덕션 환경
│   │
│   ├── backend/
│   │   └── Dockerfile
│   │
│   ├── frontend/
│   │   └── Dockerfile
│   │
│   └── nginx/
│       └── nginx.conf                 # 리버스 프록시
│
├── scripts/                           # 유틸리티 스크립트
│   ├── init_db.py                     # DB 초기화
│   ├── seed_data.py                   # 초기 데이터
│   └── deploy.sh                      # 배포 스크립트
│
├── docs/                              # 문서
│   ├── API.md                         # API 문서
│   ├── ARCHITECTURE.md                # 아키텍처 문서
│   ├── DEPLOYMENT.md                  # 배포 가이드
│   └── DEVELOPMENT.md                 # 개발 가이드
│
├── .gitignore
├── README.md
└── LICENSE
```

## 주요 디렉토리 설명

### backend/app/
- **api/**: FastAPI 라우터 및 엔드포인트
- **core/**: 핵심 설정 및 인프라 코드
- **models/**: 데이터베이스 모델 (SQLAlchemy)
- **schemas/**: API 요청/응답 스키마 (Pydantic)
- **services/**: 비즈니스 로직
- **adapters/**: 외부 API 어댑터 (Upbit 등)
- **utils/**: 공통 유틸리티

### backend/workers/
- **strategy_engine/**: 전략 로직 실행 워커
- **order_executor/**: 주문 실행 워커

### backend/strategies/
- 전략 라이브러리 (각 전략은 독립적인 모듈)
- 기본 전략 클래스를 상속받아 구현

### frontend/
- React 또는 Vue 기반 프론트엔드
- 컴포넌트, 서비스, 상태 관리 분리

### docker/
- Docker Compose 설정
- 개발/프로덕션 환경 분리

