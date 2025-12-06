# 💰 Upbit Trading Tools

Upbit 거래소 관련 유틸리티 및 백테스팅 시스템

## 📋 기능

### 1. 계좌 잔고 조회
- Upbit API를 통한 계좌 잔고 조회
- 보유 중인 암호화폐 목록 출력
- 주요 통화 (BTC, ETH, XRP 등) 필터링

### 2. 골든크로스 + RSI 필터 전략 백테스팅 ⭐ NEW!
- 골든크로스 신호에 RSI 필터를 추가하여 정확도 향상
- RSI가 과매수 구간일 때 매수 신호 필터링
- RSI가 과매도 구간일 때 매도 신호 필터링
- 가상의 돈으로 전략 시뮬레이션
- 수익률, MDD, 샤프 비율 등 상세 지표
- Buy & Hold와 비교

### 3. 실시간 가격 모니터링 ⭐ NEW!
- 5분 단위로 실시간 가격 조회
- 현재가, 변동률, 거래량 등 실시간 정보
- 여러 코인 모니터링 지원
- 커스터마이징 가능한 조회 간격

## 🚀 사용 방법

### 1. 환경 설정

```bash
# 필요한 패키지 설치
pip install PyJWT requests python-dotenv
```

### 2. API 키 설정

1. `env.example` 파일을 `.env` 로 복사
2. Upbit에서 발급받은 API 키를 입력

```bash
cp env.example .env
```

`.env` 파일 내용:
```
UPBIT_ACCESS_KEY=your_actual_access_key
UPBIT_SECRET_KEY=your_actual_secret_key
UPBIT_SERVER_URL=https://api.upbit.com
```

### 3. 실행

#### 계좌 잔고 조회
```bash
python check_balance.py
```

#### 골든크로스 + RSI 필터 전략 백테스팅
```bash
python run_backtest.py
```

**설정 변경**: `config.py` 파일을 수정하여 전략 파라미터를 조정할 수 있습니다.

#### 실시간 가격 모니터링 (5분 간격)
```bash
# 기본 사용 (비트코인, 5분 간격)
python realtime_price_monitor.py

# 다른 코인 모니터링
python realtime_price_monitor.py --market KRW-ETH

# 다른 간격으로 모니터링 (예: 1분 간격)
python realtime_price_monitor.py --interval 60
```

## 📊 출력 예시

### 계좌 잔고 조회
```
============================================================
💰 Upbit 계좌 잔고
============================================================
  KRW:    1,234,567.00000000
  BTC:         0.12345678
  ETH:         1.50000000
============================================================
```

### 백테스팅 결과
```
======================================================================
📊 백테스팅 결과
======================================================================
💰 초기 자본:      1,000,000원
💰 최종 자산:      1,250,000원
📈 총 수익률:           25.00%
📊 Buy & Hold:          20.00%
📉 MDD (최대낙폭):       -15.00%
📊 샤프 비율:             1.50
🔄 거래 횟수:              4회
🎯 승률:                75.00%
======================================================================
```

### 실시간 가격 모니터링
```
======================================================================
⏰ 2025-12-02 15:30:00
======================================================================
💰 마켓: KRW-BTC
💵 현재가: 95,000,000원
📈 변동률: +2.50% (상승)
💸 변동금액: +2,500,000원
📊 24시간 거래량: 1,234.56
📈 고가: 96,000,000원
📉 저가: 94,000,000원
======================================================================
```

## 📁 파일 구조

```
upbit_balance_checker/
├── check_balance.py              # 계좌 잔고 조회
├── run_backtest.py               # 백테스팅 실행 스크립트 ⭐
├── backtest_config.py            # 전략 설정 파일 (변경 가능)
├── strategy/                     # 전략 모듈
│   ├── __init__.py
│   ├── indicators.py            # 공통 지표 함수 (SMA, RSI 등)
│   ├── golden_cross_rsi.py      # 골든크로스 + RSI 전략
│   └── backtest_engine.py       # 백테스팅 엔진
├── realtime_price_monitor.py     # 실시간 가격 모니터링
├── requirements.txt
└── README.md
```

## 🎯 골든크로스 + RSI 필터 전략 사용법

### 기본 실행
```bash
python run_backtest.py
```

### 설정 변경 (backtest_config.py)

`backtest_config.py` 파일을 열어서 다음 값들을 변경할 수 있습니다:

```python
# 이동평균선 설정
FAST_PERIOD = 20      # 단기 이동평균 기간
SLOW_PERIOD = 50      # 장기 이동평균 기간

# RSI 설정
RSI_PERIOD = 14       # RSI 계산 기간
RSI_BUY_THRESHOLD = 50.0   # 매수 시 RSI 최대값 (이 값 이하일 때만 매수)
RSI_SELL_THRESHOLD = 70.0  # 매도 시 RSI 최소값 (이 값 이상일 때만 매도)

# 백테스트 설정
INITIAL_CASH = 1_000_000  # 초기 자본금
COMMISSION = 0.0005        # 수수료율

# 데이터 설정
MARKET = 'KRW-BTC'    # 거래할 마켓
DAYS = 365            # 수집할 일수
```

### 전략 설명

**골든크로스 + RSI 필터 전략**:
1. 골든크로스 발생 시 → 매수 신호
2. **하지만** RSI가 50 이상이면 → 매수 취소 (과매수 구간)
3. 데드크로스 발생 시 → 매도 신호
4. **하지만** RSI가 70 미만이면 → 매도 취소 (아직 과매수 아님)

이렇게 하면 **더 정확한 진입 타이밍**을 잡을 수 있습니다!

## 📡 실시간 가격 모니터링 사용법

### 기본 사용
```python
from realtime_price_monitor import PriceMonitor

# 5분 간격으로 비트코인 가격 모니터링
monitor = PriceMonitor(market='KRW-BTC', interval=300)
monitor.monitor()
```

### 커스터마이징
```python
# 다른 코인 모니터링
monitor = PriceMonitor(market='KRW-ETH', interval=300)  # 이더리움

# 다른 간격 (1분 간격)
monitor = PriceMonitor(market='KRW-BTC', interval=60)

# 10분 간격
monitor = PriceMonitor(market='KRW-BTC', interval=600)
```

### 명령줄 사용
```bash
# 기본 (비트코인, 5분)
python realtime_price_monitor.py

# 이더리움 모니터링
python realtime_price_monitor.py --market KRW-ETH

# 1분 간격
python realtime_price_monitor.py --interval 60
```

## ⚠️ 주의사항

- API 키는 절대 공개하지 마세요
- `.env` 파일은 `.gitignore`에 포함되어 있어 Git에 커밋되지 않습니다
- 조회 권한만 있는 API 키를 사용하는 것을 권장합니다
- 백테스팅 결과는 과거 데이터 기반이며, 미래 수익을 보장하지 않습니다

## 📝 라이선스

MIT License

