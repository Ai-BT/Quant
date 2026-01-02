# 퀀트 트레이딩 시스템

24시간 무중단으로 동작하는 개인 퀀트 트레이딩 시스템입니다.

## 📋 프로젝트 개요

이 시스템은 전략 로직과 주문 실행 로직을 분리하여 안정적이고 확장 가능한 트레이딩 시스템을 구축합니다.

### 주요 특징

- ✅ **24시간 무중단 운영**: Docker 기반 컨테이너 오케스트레이션
- ✅ **전략/주문 분리**: 전략 로직과 주문 실행 로직 완전 분리
- ✅ **서버 형태 운영**: FastAPI 기반 REST API + WebSocket
- ✅ **프론트엔드 제어**: React/Vue 기반 대시보드
- ✅ **확장 가능한 아키텍처**: 마이크로서비스 구조
- ✅ **다양한 전략 지원**: 전통 전략 (SMA, MACD, RSI) + AI 전략 (LSTM, Transformer, XGBoost)
- ✅ **하이브리드 전략**: 전통 전략과 AI 전략 조합 가능
- ✅ **ML 모델 관리**: 모델 학습, 추론, 버전 관리, A/B 테스트

## 🏗️ 아키텍처

자세한 아키텍처 설명은 [ARCHITECTURE.md](./ARCHITECTURE.md)를 참고하세요.

### 핵심 컴포넌트

1. **API Gateway (FastAPI)**: REST API 및 WebSocket 제공
2. **Strategy Engine Worker**: 전략 로직 실행 (전통 전략 + AI 전략)
3. **ML Model Service Worker**: AI 모델 학습 및 추론
4. **Order Executor Worker**: 실제 주문 실행
5. **Message Queue (Redis)**: 비동기 작업 큐
6. **Database (PostgreSQL)**: 영구 데이터 저장
7. **Model Storage**: 학습된 ML 모델 저장
8. **Frontend (React/Vue)**: 사용자 인터페이스

## 📁 디렉토리 구조

자세한 디렉토리 구조는 [DIRECTORY_STRUCTURE.md](./DIRECTORY_STRUCTURE.md)를 참고하세요.

```
quant_trading_system/
├── backend/          # FastAPI 백엔드
├── frontend/         # React/Vue 프론트엔드
├── docker/           # Docker 설정
├── scripts/          # 유틸리티 스크립트
└── docs/             # 문서
```

## 🔧 기술 스택

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL (메인), SQLite (초기)
- **Cache/Queue**: Redis
- **Workers**: Background tasks
- **ORM**: SQLAlchemy
- **Validation**: Pydantic

### Frontend
- **Framework**: React 또는 Vue
- **State Management**: Redux 또는 Vuex
- **Charts**: Chart.js 또는 D3.js
- **WebSocket**: Socket.io 또는 native WebSocket

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Reverse Proxy**: Nginx

## 📚 문서

- [ARCHITECTURE.md](./ARCHITECTURE.md) - 전체 아키텍처 설명
- [DIRECTORY_STRUCTURE.md](./DIRECTORY_STRUCTURE.md) - 디렉토리 구조 설계
- [COMPONENTS.md](./COMPONENTS.md) - 각 컴포넌트 상세 설명
- [AI_ML_INTEGRATION.md](./AI_ML_INTEGRATION.md) - AI/ML 통합 가이드

## 🚀 다음 단계

1. 환경 설정 및 의존성 설치
2. 데이터베이스 스키마 설계
3. API 엔드포인트 구현
4. Worker 구현
5. 전략 라이브러리 구현 (전통 전략 + AI 전략)
6. ML 모델 서비스 구현
7. 프론트엔드 구현
8. Docker 설정
9. 배포 및 모니터링

## 🤖 AI/ML 전략

이 시스템은 다음과 같은 AI/ML 전략을 지원합니다:

- **LSTM**: 시계열 데이터 기반 가격 방향 예측
- **Transformer**: 장기 의존성 학습을 통한 예측
- **XGBoost**: 다양한 특성 조합 기반 분류
- **Ensemble**: 여러 모델의 결과를 조합한 앙상블 전략

전통 전략(SMA, MACD, RSI 등)과 AI 전략을 함께 사용하여 하이브리드 전략을 구성할 수도 있습니다.

자세한 내용은 [AI_ML_INTEGRATION.md](./AI_ML_INTEGRATION.md)를 참고하세요.

## 📝 라이선스

MIT License

