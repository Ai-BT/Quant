# 전략 통합 가이드

## 개요

`quant_trading_system` 프로젝트에서 `strategies` 폴더의 전략들을 백엔드/프론트엔드에 통합하여 사용할 수 있도록 구현했습니다.

## 주요 기능

### 1. 가상 계좌 시스템
- 초기 자금: 10,000,000원 (1천만원)
- 가상 자금으로 전략을 테스트할 수 있습니다
- 매수/매도 거래 내역 관리
- 수수료 계산 (기본 0.05%)

### 2. 전략 로더
- `strategies` 폴더에서 전략을 동적으로 로드
- 전략 목록 자동 탐색
- 전략 설정 정보 읽기

### 3. 전략 실행기
- 전략 시작/중지 관리
- 비동기 실행
- 에러 처리 및 재시작 로직

## 파일 구조

```
backend/app/core/
├── virtual_account.py      # 가상 계좌 관리
├── strategy_loader.py      # 전략 로더
└── strategy_executor.py    # 전략 실행기

backend/app/api/v1/
├── strategies.py           # 전략 관리 API (업데이트됨)
└── virtual_account.py      # 가상 계좌 API (신규)
```

## API 엔드포인트

### 가상 계좌

- `GET /api/v1/virtual-account/balance` - 가상 계좌 잔고 조회
- `GET /api/v1/virtual-account/summary` - 가상 계좌 요약 정보
- `GET /api/v1/virtual-account/trades` - 거래 내역 조회
- `POST /api/v1/virtual-account/reset` - 가상 계좌 초기화

### 전략 관리 (업데이트됨)

- `GET /api/v1/strategies` - 전략 목록 조회 (실제 전략 폴더에서 로드)
- `GET /api/v1/strategies/{strategy_id}` - 전략 상세 조회
- `POST /api/v1/strategies/{strategy_id}/start` - 전략 시작
- `POST /api/v1/strategies/{strategy_id}/stop` - 전략 중지

## 사용 방법

### 1. 전략 폴더 구조

전략 폴더는 다음 구조를 가져야 합니다:

```
strategies/
├── {strategy_name}/
│   ├── __init__.py
│   ├── config.py          # 전략 설정
│   ├── strategy.py        # 전략 구현 (Strategy 클래스)
│   └── README.md          # 전략 설명 (선택)
```

### 2. 전략 클래스 구조

`strategy.py` 파일에는 전략 클래스가 있어야 합니다:

```python
class SMAStrategy:
    def __init__(self, ...):
        ...
    
    def generate_signals(self, df):
        ...
```

### 3. 전략 설정

`config.py` 파일에 전략 설정을 정의:

```python
CONFIG = {
    'name': 'SMA 골든크로스 전략',
    'market': 'KRW-BTC',
    ...
}
```

## 다음 단계

1. **전략 실행 로직 구현**
   - 실제 전략 실행 로직 (시그널 생성, 주문 실행 등)
   - 가상 계좌와 연동

2. **프론트엔드 통합**
   - 가상 계좌 정보 표시
   - 전략 선택 및 실행 UI
   - 거래 내역 표시

3. **실시간 업데이트**
   - WebSocket을 통한 실시간 업데이트
   - 전략 실행 상태 모니터링

## 참고

- 전략들은 여전히 단독으로 사용할 수 있습니다 (백테스팅 등)
- 가상 계좌는 전략 테스트를 위한 것이며, 실제 거래에는 사용되지 않습니다
- 전략 실행은 추후 Worker 프로세스에서 처리할 예정입니다



