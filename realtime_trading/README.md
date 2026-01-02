# 실시간 가상 거래 봇 (Paper Trading Bot)

골든크로스 + RSI 전략을 사용한 24시간 실시간 거래 시뮬레이션

## 특징

- **가상 거래**: 실제 돈을 사용하지 않고 가상의 돈으로 거래를 시뮬레이션
- **실시간 데이터**: Upbit API를 통해 실시간 가격 데이터 수집
- **골든크로스 + RSI 전략**: 골든크로스 신호에 RSI 필터를 추가하여 정확도 향상
- **24시간 자동 거래**: 설정한 주기마다 자동으로 시장 분석 및 거래 실행
- **로깅 및 기록**: 모든 거래 내역과 잔고 변화를 파일로 저장

## 프로젝트 구조

```
realtime_trading/
├── config.py                    # 설정 파일
├── realtime_data.py             # 실시간 데이터 수집
├── paper_trading_engine.py      # 가상 거래 엔진
├── goldcross_strategy.py        # 골든크로스 전략
├── logger.py                    # 로깅 유틸리티
├── run_realtime.py              # 메인 실행 파일
└── README.md                    # 이 파일
```

## 설치

필요한 패키지를 설치합니다:

```bash
pip install pandas requests
```

## 사용 방법

### 1. 설정 변경 (선택사항)

`config.py` 파일에서 원하는 설정을 변경할 수 있습니다:

```python
# 전략 설정
FAST_PERIOD = 20              # 단기 이동평균 기간
SLOW_PERIOD = 50              # 장기 이동평균 기간
RSI_PERIOD = 14               # RSI 계산 기간
RSI_BUY_THRESHOLD = 50.0      # 매수 시 RSI 최대값
RSI_SELL_THRESHOLD = 70.0     # 매도 시 RSI 최소값

# 가상 거래 설정
INITIAL_CASH = 1_000_000      # 초기 자본금 (100만원)
COMMISSION = 0.0005           # 수수료율 (0.05%)

# 거래 설정
MARKET = 'KRW-BTC'            # 거래할 마켓
INTERVAL = 60                 # 체크 주기 (초)
CANDLE_MINUTES = 1            # 분봉 단위
```

### 2. 봇 실행

```bash
cd realtime_trading
python run_realtime.py
```

### 3. 봇 종료

실행 중인 봇을 종료하려면 `Ctrl + C`를 누르세요. 종료 시 자동으로 거래 내역과 잔고 내역이 CSV 파일로 저장됩니다.

## 전략 설명

### 골든크로스 + RSI 전략

1. **골든크로스 매수 신호**
   - 단기 이동평균선(SMA20)이 장기 이동평균선(SMA50)을 상향 돌파
   - AND RSI가 설정한 임계값 이하 (과매수 상태가 아님)

2. **데드크로스 매도 신호**
   - 단기 이동평균선이 장기 이동평균선을 하향 돌파
   - AND RSI가 설정한 임계값 이상 (과매도 상태가 아님)

3. **RSI 필터의 역할**
   - 골든크로스가 발생해도 RSI가 너무 높으면 매수하지 않음 (과매수 방지)
   - 데드크로스가 발생해도 RSI가 너무 낮으면 매도하지 않음 (과매도 방지)

## 출력 정보

봇이 실행되면 다음과 같은 정보를 실시간으로 출력합니다:

```
[HH:MM:SS] 🟢 BUY | 📈 상승
  가격: 123,456,789원 | RSI: 45.2 | SMA: 122,000,000/120,000,000
  💰 자산: 1,050,000원 | 수익: +50,000원 (+5.00%)
  📊 거래: 10회 | 승률: 60.0%
  📝 사유: 골든크로스 발생 (RSI: 45.2)
```

- 🟢 BUY: 매수 신호
- 🔴 SELL: 매도 신호
- ⚪ HOLD: 관망
- 📈/📉: 현재 추세 (상승/하락)

## 로그 파일

모든 거래 내역과 시스템 로그는 `logs/` 디렉토리에 저장됩니다:

- `KRW-BTC_YYYYMMDD.log`: 시스템 로그
- `KRW-BTC_YYYYMMDD_trades.log`: 거래 로그
- `KRW-BTC_trades_YYYYMMDD_HHMMSS.csv`: 거래 내역 (종료 시 생성)
- `KRW-BTC_balance_YYYYMMDD_HHMMSS.csv`: 잔고 내역 (종료 시 생성)

## 주의사항

1. **실제 거래 아님**: 이 봇은 가상의 돈으로 거래를 시뮬레이션합니다. 실제 돈이 거래되지 않습니다.

2. **API 요청 제한**: Upbit API에는 초당 요청 제한이 있습니다. `INTERVAL`을 너무 짧게 설정하지 마세요.

3. **네트워크 연결**: 봇은 인터넷 연결이 필요합니다.

4. **과거 성과 ≠ 미래 성과**: 백테스트 결과가 좋다고 해서 실시간 거래에서도 같은 결과가 나오는 것은 아닙니다.

## 파라미터 최적화

다양한 파라미터 조합을 테스트하려면 `config.py`에서 값을 변경한 후 다시 실행하세요:

- `FAST_PERIOD`, `SLOW_PERIOD`: 이동평균선 기간
- `RSI_PERIOD`: RSI 계산 기간
- `RSI_BUY_THRESHOLD`, `RSI_SELL_THRESHOLD`: RSI 필터 임계값
- `CANDLE_MINUTES`: 분봉 단위 (1, 3, 5, 10, 15, 30, 60)

## 다른 코인 거래

다른 코인을 거래하려면 `config.py`에서 `MARKET` 값을 변경하세요:

```python
MARKET = 'KRW-ETH'   # 이더리움
MARKET = 'KRW-XRP'   # 리플
# 등등...
```

## 라이센스

이 프로젝트는 교육 목적으로 제작되었습니다.
