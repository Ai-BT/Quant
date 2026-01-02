# %%
# 여러 SMA 조합 비교하기
import pandas as pd
import matplotlib.pyplot as plt
import requests

# 비트코인 데이터 받기 (1년치 = 365일)
# Upbit API는 한 번에 최대 200개까지만 받을 수 있음
# 따라서 여러 번 요청해서 합치기

import time

url = "https://api.upbit.com/v1/candles/days"
headers = {"accept": "application/json"}

all_data = []
target_days = 365  # 1년 데이터
last_timestamp = None

print("📡 데이터 수집 중...")

# 200개씩 여러 번 요청
while len(all_data) < target_days:
    params = {
        'market': 'KRW-BTC',
        'count': min(200, target_days - len(all_data)),
    }
    
    # 이전 데이터의 마지막 시점부터 계속 받기
    if last_timestamp:
        params['to'] = last_timestamp
    
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    
    if not data:  # 더 이상 데이터 없음
        break
    
    all_data.extend(data)
    last_timestamp = data[-1]['candle_date_time_utc']
    
    print(f"   수집 완료: {len(all_data)}/{target_days}일")
    
    # API 요청 제한 방지 (0.1초 대기)
    time.sleep(0.1)

print(f"✅ 총 {len(all_data)}일 데이터 수집 완료!\n")

df = pd.DataFrame(all_data)
df['날짜'] = pd.to_datetime(df['candle_date_time_kst'])
df = df.sort_values('날짜')
df['종가'] = df['trade_price']

print("📊 다양한 SMA 조합 비교 분석\n")
print("="*70)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 여러 SMA 조합 테스트
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

strategies = [
    {'name': '초단기', 'fast': 5, 'slow': 20, 'emoji': '🚀'},
    {'name': '단기', 'fast': 10, 'slow': 30, 'emoji': '⚡'},
    {'name': '중기 (현재)', 'fast': 20, 'slow': 50, 'emoji': '😊'},
    {'name': '중장기', 'fast': 30, 'slow': 90, 'emoji': '🐢'},
    {'name': '장기', 'fast': 50, 'slow': 200, 'emoji': '🏔️'},
]

results = []

for strategy in strategies:
    name = strategy['name']
    fast = strategy['fast']
    slow = strategy['slow']
    emoji = strategy['emoji']
    
    # SMA 계산
    df[f'SMA{fast}'] = df['종가'].rolling(window=fast).mean()
    df[f'SMA{slow}'] = df['종가'].rolling(window=slow).mean()
    
    # 골든/데드크로스
    df['GC'] = (df[f'SMA{fast}'].shift(1) < df[f'SMA{slow}'].shift(1)) & \
               (df[f'SMA{fast}'] > df[f'SMA{slow}'])
    df['DC'] = (df[f'SMA{fast}'].shift(1) > df[f'SMA{slow}'].shift(1)) & \
               (df[f'SMA{fast}'] < df[f'SMA{slow}'])
    
    # 크로스 횟수
    gc_count = df['GC'].sum()
    dc_count = df['DC'].sum()
    total_crosses = gc_count + dc_count
    
    # 현재 상태
    latest = df.iloc[-1]
    if pd.notna(latest[f'SMA{fast}']) and pd.notna(latest[f'SMA{slow}']):
        current_trend = "상승" if latest[f'SMA{fast}'] > latest[f'SMA{slow}'] else "하락"
        gap = latest[f'SMA{fast}'] - latest[f'SMA{slow}']
        gap_percent = (gap / latest[f'SMA{slow}']) * 100
        
        # 최근 골든/데드크로스 날짜
        last_gc = df[df['GC']].iloc[-1]['날짜'] if gc_count > 0 else None
        last_dc = df[df['DC']].iloc[-1]['날짜'] if dc_count > 0 else None
        
        results.append({
            'name': name,
            'emoji': emoji,
            'fast': fast,
            'slow': slow,
            'gc_count': gc_count,
            'dc_count': dc_count,
            'total_crosses': total_crosses,
            'current_trend': current_trend,
            'gap_percent': gap_percent,
            'last_gc': last_gc,
            'last_dc': last_dc,
        })

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 결과 출력
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print(f"\n📅 분석 기간: {df.iloc[0]['날짜'].strftime('%Y-%m-%d')} ~ {df.iloc[-1]['날짜'].strftime('%Y-%m-%d')}")
print(f"📊 총 {len(df)}일 데이터\n")

for result in results:
    print("="*70)
    print(f"{result['emoji']} {result['name']} 전략: SMA{result['fast']} / SMA{result['slow']}")
    print("="*70)
    print(f"📈 골든크로스:     {result['gc_count']:>3}회")
    print(f"📉 데드크로스:     {result['dc_count']:>3}회")
    print(f"🔄 총 크로스:      {result['total_crosses']:>3}회")
    print(f"📊 현재 추세:      {result['current_trend']} ({result['gap_percent']:+.2f}%)")
    
    if result['last_gc']:
        days_since_gc = (df.iloc[-1]['날짜'] - result['last_gc']).days
        print(f"🎉 최근 골든크로스: {result['last_gc'].strftime('%Y-%m-%d')} ({days_since_gc}일 전)")
    
    if result['last_dc']:
        days_since_dc = (df.iloc[-1]['날짜'] - result['last_dc']).days
        print(f"⚠️  최근 데드크로스: {result['last_dc'].strftime('%Y-%m-%d')} ({days_since_dc}일 전)")
    
    # 평가
    if result['total_crosses'] > 20:
        print("💡 평가: 신호 너무 많음 (휩쏘 위험, 수수료 과다)")
    elif result['total_crosses'] > 10:
        print("💡 평가: 신호 많음 (단기 트레이더용)")
    elif result['total_crosses'] > 4:
        print("💡 평가: 적당한 신호 빈도 (균형 잡힘) ⭐")
    else:
        print("💡 평가: 신호 적음 (장기 투자자용)")
    
    print()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 비교 표
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("\n" + "="*70)
print("📊 전략 비교표")
print("="*70)
print(f"{'전략':<15} {'조합':<12} {'크로스':<8} {'현재 추세':<15} {'간격 %':<10}")
print("-"*70)

for result in results:
    combo = f"SMA{result['fast']}/{result['slow']}"
    trend_emoji = "📈" if result['current_trend'] == "상승" else "📉"
    print(f"{result['emoji']} {result['name']:<12} {combo:<12} {result['total_crosses']:>3}회    "
          f"{trend_emoji} {result['current_trend']:<10} {result['gap_percent']:>+7.2f}%")

print("="*70)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 추천
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("\n💡 추천 전략:")
print("-"*70)
print("🚀 초단기 (SMA5/20):   데이트레이더, 빠른 대응, 시간 많음")
print("⚡ 단기 (SMA10/30):     스윙 트레이더, 주 단위 관리")
print("😊 중기 (SMA20/50):     균형형 투자자, 월 단위 관리 ⭐ 추천!")
print("🐢 중장기 (SMA30/90):   안정 추구형, 분기 단위 관리")
print("🏔️ 장기 (SMA50/200):    장기 투자자, 큰 흐름만 추종")
print("="*70)

