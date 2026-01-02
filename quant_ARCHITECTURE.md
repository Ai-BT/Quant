# 퀀트 트레이딩 시스템 아키텍처 (AI/ML 포함)

## 1. 전체 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    Frontend (React/Vue)                              │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │    │
│  │  │  Dashboard   │  │   Strategy   │  │    Order     │  │   ML     │ │    │
│  │  │   (상태확인)  │  │   Manager    │  │   History    │  │ Dashboard│ │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └──────────┘ │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP/WebSocket
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API LAYER                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      FastAPI Server                                  │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │    │
│  │  │  REST API    │  │  WebSocket   │  │   ML API     │  │  Auth    │ │    │
│  │  │  Endpoints   │  │  Handler     │  │  (추론/학습)  │  │  (JWT)   │ │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └──────────┘ │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            │                       │                       │
            ▼                       ▼                       ▼
┌────────────────────┐  ┌────────────────────────┐  ┌──────────────────────────┐
│   SERVICE LAYER    │  │    AI/ML LAYER         │  │      DATA LAYER          │
├────────────────────┤  ├────────────────────────┤  ├──────────────────────────┤
│┌──────────────────┐│  │ ┌────────────────────┐ │  │ ┌──────────────────────┐ │
││ Strategy Service ││  │ │  Model Serving     │ │  │ │   PostgreSQL/SQLite  │ │
││ (전략 관리)       ││  │ │  (추론 서비스)      │ │  │ │   - Orders           │ │
│└──────────────────┘│  │ └────────────────────┘ │  │ │   - Positions        │ │
│┌──────────────────┐│  │ ┌────────────────────┐ │  │ │   - Strategies       │ │
││ Order Service    ││  │ │  Feature Store     │ │  │ │   - ML Predictions   │ │
││ (주문 관리)       ││  │ │  (피처 저장소)      │ │  │ │   - Training Logs    │ │
│└──────────────────┘│  │ └────────────────────┘ │  │ └──────────────────────┘ │
│┌──────────────────┐│  │ ┌────────────────────┐ │  │ ┌──────────────────────┐ │
││ Market Service   ││  │ │  Model Registry    │ │  │ │   Redis Cache        │ │
││ (시장 데이터)     ││  │ │  (모델 버전 관리)   │ │  │ │   - Real-time Data   │ │
│└──────────────────┘│  │ └────────────────────┘ │  │ │   - Feature Cache    │ │
│┌──────────────────┐│  │ ┌────────────────────┐ │  │ │   - Predictions      │ │
││ ML Service       ││  │ │  Training Pipeline │ │  │ └──────────────────────┘ │
││ (ML 관리)        ││  │ │  (학습 파이프라인)  │ │  │ ┌──────────────────────┐ │
│└──────────────────┘│  │ └────────────────────┘ │  │ │   Vector DB (선택)   │ │
└────────────────────┘  └────────────────────────┘  │ │   - Embeddings       │ │
            │                       │               │ │   - Similarity Search│ │
            │           ┌───────────┘               │ └──────────────────────┘ │
            │           │                           └──────────────────────────┘
            ▼           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            WORKER LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    Background Workers (Celery)                       │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │    │
│  │  │  Strategy    │  │   Order      │  │   Market     │  │  System  │ │    │
│  │  │  Worker      │  │   Executor   │  │   Data       │  │  Monitor │ │    │
│  │  │  (전략+ML)   │  │  (주문 실행)  │  │   Fetcher   │  │  (헬스체크)│ │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └──────────┘ │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │    │
│  │  │  ML Training │  │   Feature    │  │   Model      │               │    │
│  │  │  Worker      │  │   Engineer   │  │   Evaluator  │               │    │
│  │  │  (모델 학습)  │  │  (피처 생성)  │  │  (모델 평가)  │               │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘               │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          EXTERNAL LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │   Exchange   │  │   Broker     │  │   Market     │  │   Notification   │ │
│  │   API        │  │   API        │  │   Data API   │  │   (Slack/TG)     │ │
│  │  (거래소)     │  │  (증권사)     │  │  (시세 제공)  │  │                  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────────┘ │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                       │
│  │   News API   │  │  Sentiment   │  │  Alternative │                       │
│  │  (뉴스 데이터) │  │    API       │  │   Data API   │                       │
│  │              │  │  (감성 분석)  │  │  (대체 데이터) │                       │
│  └──────────────┘  └──────────────┘  └──────────────┘                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                       GPU COMPUTE LAYER (선택)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                     GPU Server / Cloud GPU                            │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │   │
│  │  │  Training    │  │   Inference  │  │   Batch      │  │  Model    │ │   │
│  │  │  Jobs        │  │   Server     │  │   Prediction │  │  Fine-tune│ │   │
│  │  │  (학습 작업)  │  │  (실시간 추론) │  │  (배치 예측)  │  │  (미세조정) │ │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └───────────┘ │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│  Options: Local GPU / AWS SageMaker / GCP Vertex AI / Azure ML              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 2. AI/ML 파이프라인 상세 흐름

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        AI/ML PIPELINE FLOW                                    │
└──────────────────────────────────────────────────────────────────────────────┘

1. 데이터 수집 (Data Collection)
   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
   │ Market Data │ +  │ News/Social │ +  │ Fundamental │ +  │ Alternative │
   │   (시세)    │    │   (뉴스)     │    │   (재무)    │    │   (대체)    │
   └──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
          │                  │                  │                  │
          └──────────────────┴──────────────────┴──────────────────┘
                                       │
                                       ▼
2. 피처 엔지니어링 (Feature Engineering)
   ┌────────────────────────────────────────────────────────────────────────┐
   │  Feature Engineer Worker                                               │
   │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
   │  │ Technical    │  │ Fundamental  │  │ Sentiment    │  │ Custom     │ │
   │  │ Indicators   │  │ Ratios       │  │ Features     │  │ Features   │ │
   │  │ (기술지표)    │  │ (재무비율)    │  │ (감성지표)    │  │ (사용자정의) │ │
   │  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │
   └────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
3. 피처 저장소 (Feature Store)
   ┌────────────────────────────────────────────────────────────────────────┐
   │  Feature Store (Redis + PostgreSQL)                                    │
   │  ┌──────────────────────────┐    ┌───────────────────────────────────┐ │
   │  │  Online Store (Redis)    │    │  Offline Store (PostgreSQL)       │ │
   │  │  - 실시간 추론용 피처     │    │  - 학습용 히스토리컬 피처         │ │
   │  │  - Low Latency           │    │  - 대용량 저장                    │ │
   │  └──────────────────────────┘    └───────────────────────────────────┘ │
   └────────────────────────────────────────────────────────────────────────┘
                                       │
                      ┌────────────────┴────────────────┐
                      ▼                                 ▼
4-A. 모델 학습 (Training)                4-B. 실시간 추론 (Inference)
   ┌──────────────────────────┐           ┌──────────────────────────┐
   │  Training Pipeline        │           │  Inference Service       │
   │  ┌────────────────────┐  │           │  ┌────────────────────┐  │
   │  │  Data Loader       │  │           │  │  Feature Fetcher   │  │
   │  │  (데이터 로더)      │  │           │  │  (피처 조회)        │  │
   │  └────────────────────┘  │           │  └────────────────────┘  │
   │           │              │           │           │              │
   │           ▼              │           │           ▼              │
   │  ┌────────────────────┐  │           │  ┌────────────────────┐  │
   │  │  Model Training    │  │           │  │  Model Prediction  │  │
   │  │  (모델 학습)        │  │           │  │  (예측 수행)        │  │
   │  └────────────────────┘  │           │  └────────────────────┘  │
   │           │              │           │           │              │
   │           ▼              │           │           ▼              │
   │  ┌────────────────────┐  │           │  ┌────────────────────┐  │
   │  │  Model Evaluation  │  │           │  │  Post Processing   │  │
   │  │  (성능 평가)        │  │           │  │  (후처리)          │  │
   │  └────────────────────┘  │           │  └────────────────────┘  │
   │           │              │           │           │              │
   │           ▼              │           │           ▼              │
   │  ┌────────────────────┐  │           │  ┌────────────────────┐  │
   │  │  Model Registry    │  │           │  │  Signal Generation │  │
   │  │  (모델 등록)        │  │           │  │  (신호 생성)        │  │
   │  └────────────────────┘  │           │  └────────────────────┘  │
   └──────────────────────────┘           └──────────────────────────┘
                                                     │
                                                     ▼
                                          ┌──────────────────────────┐
                                          │  Order Execution         │
                                          │  (주문 실행)              │
                                          └──────────────────────────┘
```

## 3. 디렉토리 구조 설계 (AI/ML 포함)

```
quant_trading_system/
│
├── docker/                          # Docker 관련 설정
│   ├── Dockerfile.api              # API 서버 도커파일
│   ├── Dockerfile.worker           # Worker 도커파일
│   ├── Dockerfile.ml               # ML 서비스 도커파일 (GPU 지원)
│   ├── Dockerfile.frontend         # Frontend 도커파일
│   └── docker-compose.yml          # 전체 서비스 오케스트레이션
│
├── backend/                         # 백엔드 (FastAPI)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI 앱 엔트리포인트
│   │   ├── config.py               # 환경 설정
│   │   │
│   │   ├── api/                    # API 라우터
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py         # 인증 엔드포인트
│   │   │   │   ├── strategies.py   # 전략 엔드포인트
│   │   │   │   ├── orders.py       # 주문 엔드포인트
│   │   │   │   ├── positions.py    # 포지션 엔드포인트
│   │   │   │   ├── market.py       # 시장 데이터 엔드포인트
│   │   │   │   ├── ml.py           # ⭐ ML 모델 엔드포인트 (추론/학습)
│   │   │   │   └── system.py       # 시스템 상태 엔드포인트
│   │   │   └── websocket.py        # WebSocket 핸들러
│   │   │
│   │   ├── services/               # 비즈니스 로직
│   │   │   ├── __init__.py
│   │   │   ├── strategy_service.py
│   │   │   ├── order_service.py
│   │   │   ├── market_service.py
│   │   │   ├── position_service.py
│   │   │   ├── ml_service.py       # ⭐ ML 서비스 (모델 관리, 추론 호출)
│   │   │   └── notification_service.py
│   │   │
│   │   ├── models/                 # 데이터베이스 모델
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── user.py
│   │   │   ├── strategy.py
│   │   │   ├── order.py
│   │   │   ├── position.py
│   │   │   ├── market_data.py
│   │   │   ├── ml_model.py         # ⭐ ML 모델 메타데이터
│   │   │   ├── ml_prediction.py    # ⭐ ML 예측 결과
│   │   │   └── feature.py          # ⭐ 피처 정의
│   │   │
│   │   ├── schemas/                # Pydantic 스키마
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── strategy.py
│   │   │   ├── order.py
│   │   │   ├── ml.py               # ⭐ ML 관련 스키마
│   │   │   └── feature.py          # ⭐ 피처 스키마
│   │   │
│   │   └── repositories/           # 데이터 액세스
│   │       ├── __init__.py
│   │       ├── base.py
│   │       ├── strategy_repo.py
│   │       ├── order_repo.py
│   │       └── ml_repo.py          # ⭐ ML 관련 Repository
│   │
│   ├── strategies/                 # 전략 로직
│   │   ├── __init__.py
│   │   ├── base_strategy.py
│   │   ├── momentum.py
│   │   ├── mean_reversion.py
│   │   ├── ml_strategy.py          # ⭐ ML 기반 전략 (딥러닝 신호 활용)
│   │   └── ensemble_strategy.py    # ⭐ 앙상블 전략 (Rule + ML)
│   │
│   ├── execution/                  # 주문 실행 로직
│   │   ├── __init__.py
│   │   ├── base_executor.py
│   │   ├── paper_executor.py
│   │   ├── live_executor.py
│   │   └── brokers/
│   │       ├── __init__.py
│   │       ├── base_broker.py
│   │       ├── kiwoom.py
│   │       ├── kis.py
│   │       └── binance.py
│   │
│   ├── workers/                    # 백그라운드 워커
│   │   ├── __init__.py
│   │   ├── celery_app.py
│   │   ├── tasks/
│   │   │   ├── __init__.py
│   │   │   ├── strategy_tasks.py
│   │   │   ├── order_tasks.py
│   │   │   ├── market_tasks.py
│   │   │   ├── system_tasks.py
│   │   │   ├── ml_training_tasks.py    # ⭐ 모델 학습 태스크
│   │   │   ├── ml_inference_tasks.py   # ⭐ 배치 추론 태스크
│   │   │   └── feature_tasks.py        # ⭐ 피처 엔지니어링 태스크
│   │   └── schedulers/
│   │       ├── __init__.py
│   │       └── beat_schedule.py
│   │
│   └── tests/
│       ├── unit/
│       └── integration/
│
├── ml/                              # ⭐ ML/딥러닝 모듈 (독립 모듈)
│   ├── __init__.py
│   │
│   ├── features/                   # ⭐ 피처 엔지니어링
│   │   ├── __init__.py
│   │   ├── base_feature.py         # 피처 베이스 클래스
│   │   ├── technical.py            # 기술적 지표 피처
│   │   ├── fundamental.py          # 재무 피처
│   │   ├── sentiment.py            # 감성 분석 피처
│   │   ├── time_features.py        # 시간 관련 피처
│   │   └── feature_store.py        # 피처 스토어 연동
│   │
│   ├── models/                     # ⭐ 딥러닝 모델 정의
│   │   ├── __init__.py
│   │   ├── base_model.py           # 모델 베이스 클래스
│   │   │
│   │   ├── price_prediction/       # 가격 예측 모델
│   │   │   ├── __init__.py
│   │   │   ├── lstm.py             # LSTM 모델
│   │   │   ├── transformer.py      # Transformer 모델
│   │   │   ├── tcn.py              # Temporal CNN
│   │   │   └── nbeats.py           # N-BEATS 모델
│   │   │
│   │   ├── signal_classification/ # 신호 분류 모델
│   │   │   ├── __init__.py
│   │   │   ├── cnn_classifier.py   # CNN 기반 분류기
│   │   │   └── attention_classifier.py  # Attention 기반 분류기
│   │   │
│   │   ├── reinforcement/          # 강화학습 모델
│   │   │   ├── __init__.py
│   │   │   ├── dqn.py              # DQN
│   │   │   ├── ppo.py              # PPO
│   │   │   └── a2c.py              # A2C
│   │   │
│   │   └── ensemble/               # 앙상블 모델
│   │       ├── __init__.py
│   │       └── stacking.py         # 스태킹 앙상블
│   │
│   ├── training/                   # ⭐ 학습 파이프라인
│   │   ├── __init__.py
│   │   ├── trainer.py              # 학습 메인 로직
│   │   ├── data_loader.py          # 데이터 로더
│   │   ├── callbacks.py            # 학습 콜백 (Early Stopping 등)
│   │   ├── loss_functions.py       # 커스텀 손실 함수
│   │   ├── optimizers.py           # 옵티마이저 설정
│   │   └── hyperparameter_tuning.py # 하이퍼파라미터 튜닝
│   │
│   ├── inference/                  # ⭐ 추론 서비스
│   │   ├── __init__.py
│   │   ├── inference_engine.py     # 추론 엔진
│   │   ├── model_loader.py         # 모델 로더
│   │   ├── preprocessing.py        # 전처리
│   │   ├── postprocessing.py       # 후처리
│   │   └── batch_inference.py      # 배치 추론
│   │
│   ├── registry/                   # ⭐ 모델 레지스트리
│   │   ├── __init__.py
│   │   ├── model_registry.py       # 모델 버전 관리
│   │   ├── artifact_store.py       # 아티팩트 저장소
│   │   └── experiment_tracker.py   # 실험 추적 (MLflow 연동)
│   │
│   ├── evaluation/                 # ⭐ 모델 평가
│   │   ├── __init__.py
│   │   ├── metrics.py              # 평가 지표 (Sharpe, Sortino 등)
│   │   ├── backtester.py           # 백테스트
│   │   └── model_monitor.py        # 모델 드리프트 모니터링
│   │
│   ├── serving/                    # ⭐ 모델 서빙 (별도 서버)
│   │   ├── __init__.py
│   │   ├── server.py               # 추론 서버 (FastAPI/gRPC)
│   │   ├── request_handler.py      # 요청 핸들러
│   │   └── health_check.py         # 헬스 체크
│   │
│   ├── utils/                      # 유틸리티
│   │   ├── __init__.py
│   │   ├── gpu_utils.py            # GPU 관리
│   │   ├── data_utils.py           # 데이터 처리
│   │   └── visualization.py        # 시각화
│   │
│   ├── configs/                    # ML 설정
│   │   ├── model_configs/          # 모델별 설정
│   │   │   ├── lstm_config.yaml
│   │   │   ├── transformer_config.yaml
│   │   │   └── dqn_config.yaml
│   │   └── training_config.yaml    # 학습 설정
│   │
│   ├── notebooks/                  # Jupyter 노트북 (실험용)
│   │   ├── 01_data_exploration.ipynb
│   │   ├── 02_feature_engineering.ipynb
│   │   ├── 03_model_training.ipynb
│   │   └── 04_backtesting.ipynb
│   │
│   └── requirements-ml.txt         # ML 전용 의존성
│
├── frontend/                       # 프론트엔드
│   ├── src/
│   │   ├── components/
│   │   │   ├── ml/                 # ⭐ ML 관련 컴포넌트
│   │   │   │   ├── ModelDashboard.jsx    # 모델 대시보드
│   │   │   │   ├── PredictionChart.jsx   # 예측 차트
│   │   │   │   ├── ModelPerformance.jsx  # 모델 성능
│   │   │   │   ├── FeatureImportance.jsx # 피처 중요도
│   │   │   │   └── TrainingProgress.jsx  # 학습 진행률
│   │   │   ├── dashboard/
│   │   │   ├── strategy/
│   │   │   └── charts/
│   │   │
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Strategies.jsx
│   │   │   ├── MLModels.jsx        # ⭐ ML 모델 관리 페이지
│   │   │   └── Predictions.jsx     # ⭐ 예측 결과 페이지
│   │   │
│   │   └── services/
│   │       ├── api.js
│   │       ├── mlApi.js            # ⭐ ML API 서비스
│   │       └── websocketService.js
│   │
│   └── package.json
│
├── data/                           # 데이터 디렉토리
│   ├── raw/                        # 원본 데이터
│   ├── processed/                  # 전처리된 데이터
│   ├── features/                   # ⭐ 피처 데이터
│   ├── models/                     # ⭐ 학습된 모델 저장
│   │   ├── checkpoints/            # 체크포인트
│   │   └── production/             # 운영 모델
│   └── experiments/                # ⭐ 실험 결과
│
├── mlflow/                         # ⭐ MLflow 설정 (선택)
│   └── mlflow.db                   # MLflow 트래킹 DB
│
├── scripts/
│   ├── start.sh
│   ├── train_model.sh              # ⭐ 모델 학습 스크립트
│   └── deploy_model.sh             # ⭐ 모델 배포 스크립트
│
├── configs/
│   ├── development.yaml
│   ├── production.yaml
│   └── ml_production.yaml          # ⭐ ML 운영 설정
│
├── .env.example
├── README.md
└── ARCHITECTURE.md
```

## 4. AI/ML 컴포넌트 역할 설명

### 4.1 Feature Store (피처 저장소)

| 컴포넌트 | 역할 |
|---------|------|
| **Online Store (Redis)** | 실시간 추론을 위한 저지연 피처 저장소 |
| **Offline Store (PostgreSQL)** | 학습용 대용량 히스토리컬 피처 저장소 |
| **Feature Engineering Worker** | 원시 데이터에서 피처 생성 및 저장 |

### 4.2 Model Registry (모델 레지스트리)

| 컴포넌트 | 역할 |
|---------|------|
| **Model Versioning** | 모델 버전 관리 (v1, v2, ...) |
| **Artifact Store** | 모델 가중치, 설정 파일 저장 |
| **Experiment Tracking** | 실험 결과 추적 (MLflow 연동) |
| **Model Staging** | 모델 상태 관리 (Staging → Production) |

### 4.3 Training Pipeline (학습 파이프라인)

| 컴포넌트 | 역할 |
|---------|------|
| **Data Loader** | 학습 데이터 로드 및 배치 처리 |
| **Trainer** | 모델 학습 실행 |
| **Hyperparameter Tuning** | 하이퍼파라미터 최적화 (Optuna 등) |
| **Model Evaluation** | 학습 후 성능 평가 |

### 4.4 Inference Service (추론 서비스)

| 컴포넌트 | 역할 |
|---------|------|
| **Model Loader** | 운영 모델 로드 |
| **Preprocessing** | 입력 데이터 전처리 |
| **Prediction** | 모델 추론 실행 |
| **Postprocessing** | 예측 결과 후처리 (신호 변환) |

### 4.5 딥러닝 모델 종류

| 모델 유형 | 용도 | 예시 |
|----------|------|------|
| **Price Prediction** | 가격/수익률 예측 | LSTM, Transformer, N-BEATS |
| **Signal Classification** | 매수/매도/홀드 분류 | CNN Classifier, Attention |
| **Reinforcement Learning** | 포트폴리오 최적화 | DQN, PPO, A2C |
| **Sentiment Analysis** | 뉴스/소셜 감성 분석 | BERT, FinBERT |

## 5. AI 기반 전략 vs 기존 전략 비교

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Rule-based Strategy (기존)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Market Data → Technical Indicators → Rule Logic → Signal                  │
│       │              │                    │           │                     │
│   [OHLCV]    [RSI, MACD, MA]     [if RSI<30: BUY]   [BUY/SELL]             │
│                                                                             │
│  장점: 해석 가능, 빠른 실행, 로직 명확                                       │
│  단점: 복잡한 패턴 인식 어려움, 수동 규칙 작성 필요                           │
└─────────────────────────────────────────────────────────────────────────────┘

                                    VS

┌─────────────────────────────────────────────────────────────────────────────┐
│                     ML-based Strategy (AI 기반)                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Market Data → Feature Engineering → ML Model → Prediction → Signal        │
│       │              │                  │           │           │           │
│   [OHLCV]    [100+ Features]      [LSTM/Trans]  [0.73 prob]  [BUY]         │
│   [News]     [Embeddings]                                                   │
│   [Sentiment]                                                               │
│                                                                             │
│  장점: 복잡한 패턴 학습, 비정형 데이터 활용, 자동화된 특징 추출               │
│  단점: 해석 어려움, 학습 시간/비용, 오버피팅 위험                             │
└─────────────────────────────────────────────────────────────────────────────┘

                                    BEST

┌─────────────────────────────────────────────────────────────────────────────┐
│                     Hybrid Strategy (Rule + AI)                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌────────────────────┐   ┌────────────────────┐                           │
│  │ Rule-based Signal  │   │  ML-based Signal   │                           │
│  │  (0.6 confidence)  │   │  (0.73 confidence) │                           │
│  └─────────┬──────────┘   └─────────┬──────────┘                           │
│            │                        │                                       │
│            └────────────┬───────────┘                                       │
│                         ▼                                                   │
│            ┌────────────────────────┐                                       │
│            │   Ensemble / Voting    │                                       │
│            │   (앙상블 결합)         │                                       │
│            └────────────────────────┘                                       │
│                         │                                                   │
│                         ▼                                                   │
│            ┌────────────────────────┐                                       │
│            │   Final Signal (BUY)   │                                       │
│            └────────────────────────┘                                       │
│                                                                             │
│  장점: 두 접근법의 장점 결합, 신호 검증, 더 안정적인 성과                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 6. 기술 스택 상세 (AI/ML 포함)

| 영역 | 기술 | 용도 |
|------|------|------|
| **Backend** | FastAPI | REST API, WebSocket 서버 |
| **Task Queue** | Celery + Redis | 백그라운드 작업 처리 |
| **Database** | PostgreSQL | 영구 데이터 저장, Offline Feature Store |
| **Cache** | Redis | Online Feature Store, 세션, 캐싱 |
| **ML Framework** | PyTorch / TensorFlow | 딥러닝 모델 개발 |
| **Feature Store** | Feast (선택) 또는 Custom | 피처 관리 |
| **Experiment Tracking** | MLflow / Weights & Biases | 실험 추적, 모델 레지스트리 |
| **Hyperparameter Tuning** | Optuna / Ray Tune | 하이퍼파라미터 최적화 |
| **Model Serving** | FastAPI / TorchServe / Triton | 모델 서빙 |
| **GPU Compute** | Local GPU / AWS SageMaker / GCP Vertex AI | GPU 학습/추론 |
| **Frontend** | React + Vite | 웹 대시보드 |
| **Charts** | Plotly / Lightweight Charts | 시각화 |
| **Deployment** | Docker + Docker Compose / K8s | 컨테이너 기반 배포 |

## 7. ML 파이프라인 운영 주기

```
┌────────────────────────────────────────────────────────────────────────────┐
│                          ML Lifecycle                                       │
└────────────────────────────────────────────────────────────────────────────┘

1. 데이터 수집 (지속적)
   └── Market Data Fetcher → PostgreSQL

2. 피처 생성 (매 분/시간)
   └── Feature Engineer → Feature Store

3. 모델 학습 (일간/주간/이벤트 기반)
   └── Training Pipeline → Model Registry

4. 모델 평가 (학습 후)
   └── Backtester → 성능 지표 확인

5. 모델 배포 (수동/자동)
   └── Staging → Production 승격

6. 실시간 추론 (24시간)
   └── Inference Service → Trading Signal

7. 모델 모니터링 (지속적)
   └── Model Monitor → 드리프트 감지 → 재학습 트리거

┌────────────────────────────────────────────────────────────────────────────┐
│  스케줄 예시:                                                               │
│  - 피처 생성: 매 1분                                                        │
│  - 배치 추론: 매 5분                                                        │
│  - 모델 재학습: 매일 장 마감 후 (자동) 또는 성능 저하 시 (트리거)            │
│  - 모델 평가: 매주                                                          │
└────────────────────────────────────────────────────────────────────────────┘
```

## 8. 다음 단계 (AI/ML 포함)

1. **Phase 1**: 기본 구조 설정 (FastAPI 서버, DB, Docker)
2. **Phase 2**: 전략 모듈 개발 (Rule-based 먼저)
3. **Phase 3**: 주문 실행 모듈 개발 (Paper Trading)
4. **Phase 4**: Worker 개발 (Celery)
5. **Phase 5**: ML 파이프라인 구축
   - Feature Store 구현
   - 학습 파이프라인 구현
   - 추론 서비스 구현
6. **Phase 6**: ML 모델 개발
   - 가격 예측 모델 (LSTM/Transformer)
   - 신호 분류 모델
   - 하이브리드 전략 구현
7. **Phase 7**: Frontend 개발 (Dashboard + ML 모니터링)
8. **Phase 8**: 실제 거래 연동
9. **Phase 9**: 배포 및 운영 (Docker, GPU 서버)
