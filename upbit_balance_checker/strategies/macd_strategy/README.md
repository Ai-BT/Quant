# MACD + Trend Filter 전략

## 📚 전략 개념

### 1. MACD (Moving Average Convergence Divergence)

**이동평균 수렴·확산 지표**로, 두 개의 이동평균선 간의 관계를 나타내는 모멘텀 지표입니다.

#### 🔢 MACD 구성 요소

1. **MACD Line (기준선)**
   ```
   MACD Line = 12일 EMA - 26일 EMA
   ```
   - 단기 추세와 장기 추세의 차이
   - 양수면 상승 추세, 음수면 하락 추세

2. **Signal Line (신호선)**
   ```
   Signal Line = MACD Line의 9일 EMA
   ```
   - MACD의 이동평균
   - 매매 시점을 포착하는 기준선

3. **Histogram (히스토그램)**
   ```
   Histogram = MACD Line - Signal Line
   ```
   - 두 선의 차이를 막대그래프로 표현
   - 추세의 강도를 시각적으로 표현

#### 📈 MACD 매매 신호

**골든 크로스 (매수 신호)**
```
MACD Line이 Signal Line을 위로 돌파
→ 히스토그램이 음수에서 양수로 전환
```

**데드 크로스 (매도 신호)**
```
MACD Line이 Signal Line을 아래로 돌파
→ 히스토그램이 양수에서 음수로 전환
```

---

### 2. Trend Filter (추세 필터)

#### 🤔 왜 필요한가?

MACD만 단독으로 사용하면:
- ❌ **횡보장**(옆으로 움직이는 시장)에서 **거짓 신호** 다발
- ❌ 작은 움직임에도 민감하게 반응
- ❌ 큰 추세를 놓칠 수 있음

#### ✅ Trend Filter의 역할

큰 그림의 추세 방향을 확인하여, **추세에 순응하는 매매**만 허용

---

## 🎯 전략 로직

### 매수 조건 (모두 만족 시)

```python
1. MACD Line > Signal Line (골든크로스)
2. 현재가 > 200일 SMA (상승 추세 확인)
3. MACD Histogram > 0 (추세 강도 확인) [선택]
```

### 매도 조건 (하나라도 만족 시)

```python
1. MACD Line < Signal Line (데드크로스)
2. 현재가 < 200일 SMA (추세 반전)
```

---

## 📁 파일 구조

```
macd_strategy/
├── config.py          # 전략 설정 (파라미터 변경)
├── strategy.py        # 전략 구현 (MACD, Trend Filter 계산)
├── run_macd.py        # 실행 파일
└── README.md          # 이 문서
```

---

## 🚀 사용 방법

### 1. 기본 실행

```bash
cd strategies/macd_strategy
python run_macd.py
```

### 2. 설정 변경

`config.py`에서 원하는 설정을 선택하거나 수정:

```python
# 기본 MACD + 200일 SMA Trend Filter
from config import MACD_TREND_CONFIG as cfg

# 이중 트렌드 필터 (50일 + 200일)
from config import MACD_DUAL_TREND_CONFIG as cfg

# Volume Filter 추가
from config import MACD_VOLUME_CONFIG as cfg

# MACD 단독 (비교용)
from config import MACD_ONLY_CONFIG as cfg
```

---

## ⚙️ 주요 설정 파라미터

### MACD 설정

| 파라미터 | 기본값 | 설명 |
|---------|-------|------|
| `macd_fast` | 12 | MACD 단기 EMA 기간 |
| `macd_slow` | 26 | MACD 장기 EMA 기간 |
| `macd_signal` | 9 | Signal Line EMA 기간 |

### Trend Filter 설정

| 파라미터 | 기본값 | 설명 |
|---------|-------|------|
| `trend_ma_period` | 200 | 추세 확인용 MA 기간 |
| `trend_ma_type` | 'SMA' | MA 종류 ('SMA' or 'EMA') |
| `use_dual_trend` | False | 이중 트렌드 필터 사용 |
| `mid_trend_period` | 50 | 중기 트렌드 MA 기간 |

### 추가 필터

| 파라미터 | 기본값 | 설명 |
|---------|-------|------|
| `use_histogram_filter` | True | Histogram > 0 조건 |
| `min_histogram` | 0 | 최소 Histogram 값 |
| `use_volume_filter` | False | 거래량 필터 사용 |
| `volume_multiplier` | 1.2 | 평균 거래량 대비 배수 |

### 백테스팅 설정

| 파라미터 | 기본값 | 설명 |
|---------|-------|------|
| `initial_cash` | 1,000,000 | 초기 자본금 |
| `commission` | 0.0005 | 거래 수수료 (0.05%) |
| `market` | 'KRW-BTC' | 마켓 코드 |
| `candles_count` | 500 | 데이터 개수 (최소 200 권장) |

---

## 📊 전략 변형

### 1. MACD + 200일 SMA (기본, 추천)

```python
MACD_TREND_CONFIG = {
    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9,
    'trend_ma_period': 200,
    'use_histogram_filter': True,
}
```

**특징**: 가장 검증되고 안정적인 설정

---

### 2. MACD + 이중 트렌드 (보수적)

```python
MACD_DUAL_TREND_CONFIG = {
    'trend_ma_period': 200,      # 장기 추세
    'mid_trend_period': 50,      # 중기 추세
    'use_dual_trend': True,
}
```

**매수 조건**: 50일 MA > 200일 MA (정배열) + 기존 조건

**특징**: 더 강한 상승 추세에서만 매수 → 거래 횟수↓, 안정성↑

---

### 3. MACD + Volume Filter (공격적)

```python
MACD_VOLUME_CONFIG = {
    'use_volume_filter': True,
    'volume_ma_period': 20,
    'volume_multiplier': 1.2,    # 평균 거래량의 1.2배 이상
}
```

**특징**: 거래량 급증 시에만 매수 → 강한 신호 포착

---

### 4. MACD 단독 (비교용)

```python
MACD_ONLY_CONFIG = {
    'use_trend_filter': False,
    'use_histogram_filter': False,
}
```

**특징**: Trend Filter 없이 순수 MACD만 사용 → 거래 횟수↑, 거짓 신호↑

---

## ⚖️ 전략 장단점

### ✅ 장점

1. **거짓 신호 감소**: Trend Filter로 횡보장 신호 필터링
2. **추세 순응**: 큰 추세에 맞춰 매매하여 수익률 증가
3. **명확한 기준**: 객관적인 진입/청산 조건
4. **검증된 방법**: 전통적이고 널리 사용되는 전략

### ❌ 단점

1. **후행성**: 이동평균 기반이라 신호가 늦을 수 있음
2. **급변 취약**: 급격한 추세 전환 시 대응 느림
3. **횡보장 불리**: 추세가 없으면 거래 기회가 적음
4. **최적값 의존**: 매개변수 선택이 수익에 영향

---

## 📈 실전 예시

### 매수 시점

```
날짜: 2024-01-15
가격: 52,000,000원
200일 SMA: 48,000,000원
MACD: +150
Signal: +50
Histogram: +100

판단:
✅ 가격 > 200일 SMA → 상승 추세
✅ MACD > Signal → 골든크로스
✅ Histogram > 0 → 모멘텀 강함
→ 💰 매수!
```

### 매도 시점

```
날짜: 2024-03-20
가격: 47,000,000원
200일 SMA: 48,000,000원
MACD: -80
Signal: +20

판단:
❌ 가격 < 200일 SMA → 추세 반전
❌ MACD < Signal → 데드크로스
→ 📉 매도!
```

---

## 💡 최적화 팁

### 1. 코인별 파라미터 조정

변동성이 큰 알트코인:
```python
'macd_fast': 8,      # 더 빠른 반응
'macd_slow': 21,
'trend_ma_period': 100,  # 더 짧은 추세
```

안정적인 비트코인:
```python
'macd_fast': 12,     # 표준 설정
'macd_slow': 26,
'trend_ma_period': 200,
```

### 2. 시장 상황별 전략

**강한 상승장**: 
- Histogram Filter 제거 → 빠른 진입

**횡보장**:
- 이중 Trend Filter 사용 → 거짓 신호 차단

**변동성 장**:
- Volume Filter 추가 → 강한 신호만 포착

---

## 📝 출력 파일

### 1. 로그 파일 (.log)

```
logs/MACD_Trend_Filter_KRW-BTC_20241215_143021.log
```

실시간 실행 로그

### 2. 결과 리포트 (.txt)

```
results/MACD_Trend_Filter_KRW-BTC_20241215_143021.txt
```

백테스팅 상세 결과 요약

### 3. 거래 내역 (.csv)

```
results/MACD_Trend_Filter_KRW-BTC_20241215_143021_trades.csv
```

모든 거래 내역 (날짜, 유형, 가격, 수량 등)

---

## 🔬 백테스팅 지표 해석

### 수익률
- **총 수익률**: 전략의 절대 수익률
- **Buy&Hold 수익률**: 매수 후 보유 시 수익률
- **초과 수익**: 전략 수익률 - Buy&Hold 수익률

### 리스크
- **MDD**: 최대 낙폭 (낮을수록 좋음)
- **Sharpe Ratio**: 위험 대비 수익 (높을수록 좋음, 1 이상 양호)

### 거래
- **총 거래 횟수**: 많을수록 수수료 부담↑
- **승률**: 수익 거래 비율 (50% 이상이면 양호)

---

## 🎓 추가 학습 자료

### MACD 기본 개념
- [Investopedia - MACD](https://www.investopedia.com/terms/m/macd.asp)

### Trend Following
- "Trend Following" by Michael Covel
- 추세 추종 전략의 원리와 실전

### 백테스팅 주의사항
- 과최적화(Overfitting) 경계
- 거래 비용 반드시 고려
- 다양한 시장 구간에서 테스트

---

## 📞 문의 및 개선

전략 개선 아이디어나 버그 리포트는 이슈로 등록해주세요!

**Happy Trading! 📈🚀**

