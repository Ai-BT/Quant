# 📈 SMA 골든크로스 전략

단순 이동평균선(SMA)의 크로스를 이용한 매매 전략

## 📋 전략 종류

### 1. SMA 5/20 (일봉)
- **특징**: 빠른 반응, 단기 트레이딩
- **적합**: 변동성이 큰 시장
- **거래 빈도**: 높음

### 2. SMA 20/50 (일봉)
- **특징**: 안정적인 신호, 중장기 투자
- **적합**: 추세가 명확한 시장
- **거래 빈도**: 중간

### 3. SMA 분봉 전략 (5캔들/30캔들)
- **특징**: 초단기 트레이딩, 1분봉 기반
- **적합**: 당일 매매, 단기 트레이딩
- **거래 빈도**: 1시간 간격 (조절 가능)
- **참고**: 5개 캔들 vs 30개 캔들 평균 비교

## 🚀 사용 방법

### SMA 5/20 전략 실행 (일봉)
```bash
cd strategies/sma_strategy
python run_sma5_20.py
```

### SMA 20/50 전략 실행 (일봉)
```bash
cd strategies/sma_strategy
python run_sma20_50.py
```

### SMA 분봉 전략 실행 (1분봉 데이터)
```bash
cd strategies/sma_strategy
python run_sma_minute.py
```

## ⚙️ 설정 변경

`config.py` 파일을 수정하세요:

```python
# 일봉 전략
SMA5_20_CONFIG = {
    'market': 'KRW-ETH',       # 이더리움으로 변경
    'fast_period': 7,          # 7일로 변경
    'slow_period': 25,         # 25일로 변경
    'initial_cash': 5_000_000, # 500만원
}

# 분봉 전략
SMA_MINUTE_CONFIG = {
    'market': 'KRW-SOL',       # 솔라나로 변경
    'fast_period': 5,          # 5개 캔들
    'slow_period': 30,         # 30개 캔들
    'trade_interval': 30,      # 30분마다 거래 (더 자주)
    'candles_count': 2000,     # 더 많은 데이터
}
```

## 📊 전략 설명

### 골든크로스 (Golden Cross)
- **발생**: 단기 이동평균선이 장기 이동평균선을 위로 돌파
- **신호**: 매수
- **의미**: 상승 추세 시작

### 데드크로스 (Dead Cross)
- **발생**: 단기 이동평균선이 장기 이동평균선을 아래로 돌파
- **신호**: 매도
- **의미**: 하락 추세 시작

## 📁 파일 구조

```
sma_strategy/
├── __init__.py
├── config.py          # 전략 설정 (3가지 전략)
├── strategy.py        # 전략 구현
├── run_sma5_20.py     # SMA 5/20 실행 (일봉)
├── run_sma20_50.py    # SMA 20/50 실행 (일봉)
├── run_sma_minute.py  # SMA 분봉 실행 (1분봉)
└── README.md
```

## 💡 팁

1. **시장 상황에 맞는 전략 선택**
   - 변동성 큰 시장: SMA 5/20
   - 안정적인 추세: SMA 20/50

2. **코인별 최적화**
   - 코인마다 최적 파라미터가 다름
   - 여러 설정으로 백테스팅 후 선택

3. **리스크 관리**
   - 초기 자본의 일부만 사용
   - 손절/익절 규칙 추가 고려

