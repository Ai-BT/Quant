# %%
# 여러 SMA 전략 백테스팅 - 실제 수익률 비교
import pandas as pd
import matplotlib.pyplot as plt
import requests
import time
import numpy as np
import warnings

# matplotlib 폰트 경고 숨기기
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

print("="*70)
print("🚀 SMA 전략 백테스팅 시스템")
print("="*70)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. 데이터 수집 (1년)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

url = "https://api.upbit.com/v1/candles/days"
headers = {"accept": "application/json"}

all_data = []
target_days = 365
last_timestamp = None

print("\n📡 데이터 수집 중...")

while len(all_data) < target_days:
    params = {
        'market': 'KRW-XRP',
        'count': min(200, target_days - len(all_data)),
    }
    
    if last_timestamp:
        params['to'] = last_timestamp
    
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    
    if not data:
        break
    
    all_data.extend(data)
    last_timestamp = data[-1]['candle_date_time_utc']
    print(f"   수집: {len(all_data)}/{target_days}일")
    time.sleep(0.1)

print(f"✅ 총 {len(all_data)}일 데이터 수집 완료!\n")

df = pd.DataFrame(all_data)
df['날짜'] = pd.to_datetime(df['candle_date_time_kst'])
df = df.sort_values('날짜').reset_index(drop=True)
df['종가'] = df['trade_price']

print(f"📅 분석 기간: {df.iloc[0]['날짜'].strftime('%Y-%m-%d')} ~ {df.iloc[-1]['날짜'].strftime('%Y-%m-%d')}")
print(f"📊 시작 가격: {df.iloc[0]['종가']:,.0f}원")
print(f"📊 종료 가격: {df.iloc[-1]['종가']:,.0f}원")

# Buy & Hold 수익률
buy_hold_return = ((df.iloc[-1]['종가'] / df.iloc[0]['종가']) - 1) * 100
print(f"💰 Buy & Hold 수익률: {buy_hold_return:+.2f}%\n")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. 전략 정의
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

strategies = [
    {'name': '초단기', 'fast': 5, 'slow': 20, 'emoji': '🚀'},
    {'name': '단기', 'fast': 10, 'slow': 30, 'emoji': '⚡'},
    {'name': '중기', 'fast': 20, 'slow': 50, 'emoji': '😊'},
    {'name': '중장기', 'fast': 30, 'slow': 90, 'emoji': '🐢'},
    {'name': '장기', 'fast': 50, 'slow': 200, 'emoji': '🏔️'},
]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. 백테스팅 함수
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def backtest_strategy(df, fast, slow, initial_cash=1000000, commission=0.0005):
    """
    SMA 전략 백테스팅
    
    Parameters:
    -----------
    df : DataFrame
        가격 데이터
    fast : int
        단기 이동평균 기간
    slow : int
        장기 이동평균 기간
    initial_cash : float
        초기 자본 (기본 100만원)
    commission : float
        수수료율 (기본 0.05%)
    
    Returns:
    --------
    dict
        백테스팅 결과
    """
    
    df = df.copy()
    
    # SMA 계산
    df['SMA_fast'] = df['종가'].rolling(window=fast).mean()
    df['SMA_slow'] = df['종가'].rolling(window=slow).mean()
    
    # 신호 생성
    df['signal'] = 0
    df.loc[df['SMA_fast'] > df['SMA_slow'], 'signal'] = 1  # 매수
    df.loc[df['SMA_fast'] <= df['SMA_slow'], 'signal'] = 0  # 매도
    
    # 포지션 변화 (실제 거래 시점)
    df['position'] = df['signal'].diff()
    
    # 백테스팅 변수
    cash = initial_cash
    holdings = 0  # 보유 코인 수
    portfolio_value = []
    trades = []
    
    for i in range(len(df)):
        price = df.iloc[i]['종가']
        position = df.iloc[i]['position']
        
        # 매수 신호
        if position == 1 and cash > 0:
            # 현금으로 살 수 있는 만큼 매수
            buy_amount = cash * (1 - commission)  # 수수료 제외
            holdings = buy_amount / price
            trades.append({
                'date': df.iloc[i]['날짜'],
                'type': 'BUY',
                'price': price,
                'amount': buy_amount,
                'holdings': holdings
            })
            cash = 0
        
        # 매도 신호
        elif position == -1 and holdings > 0:
            # 보유 코인 전량 매도
            sell_amount = holdings * price * (1 - commission)  # 수수료 제외
            trades.append({
                'date': df.iloc[i]['날짜'],
                'type': 'SELL',
                'price': price,
                'amount': sell_amount,
                'holdings': 0
            })
            cash = sell_amount
            holdings = 0
        
        # 현재 포트폴리오 가치
        current_value = cash + (holdings * price)
        portfolio_value.append(current_value)
    
    # 최종 정산 (아직 보유 중이면 매도)
    if holdings > 0:
        final_price = df.iloc[-1]['종가']
        cash = holdings * final_price * (1 - commission)
        holdings = 0
    
    final_value = cash
    total_return = ((final_value / initial_cash) - 1) * 100
    
    # 수익률 계산
    df['portfolio_value'] = portfolio_value
    df['returns'] = df['portfolio_value'].pct_change()
    
    # 최대 낙폭 (MDD)
    cummax = df['portfolio_value'].expanding().max()
    drawdown = (df['portfolio_value'] - cummax) / cummax
    mdd = drawdown.min() * 100
    
    # 샤프 비율 (암호화폐는 365일 거래)
    risk_free_rate = 0.02 / 365  # 일별 무위험 수익률 (암호화폐 = 365일)
    excess_returns = df['returns'] - risk_free_rate
    sharpe_ratio = (excess_returns.mean() / excess_returns.std()) * np.sqrt(365) if excess_returns.std() != 0 else 0
    
    # 승률
    winning_trades = len([t for t in trades if t['type'] == 'SELL'])
    if winning_trades > 0:
        profits = []
        for i in range(0, len(trades)-1, 2):
            if i+1 < len(trades) and trades[i]['type'] == 'BUY' and trades[i+1]['type'] == 'SELL':
                profit = trades[i+1]['amount'] - trades[i]['amount']
                profits.append(profit)
        
        win_count = len([p for p in profits if p > 0])
        win_rate = (win_count / len(profits) * 100) if len(profits) > 0 else 0
    else:
        win_rate = 0
    
    return {
        'initial_cash': initial_cash,
        'final_value': final_value,
        'total_return': total_return,
        'mdd': mdd,
        'sharpe_ratio': sharpe_ratio,
        'num_trades': len(trades),
        'win_rate': win_rate,
        'trades': trades,
        'portfolio_values': df['portfolio_value'].tolist(),
        'dates': df['날짜'].tolist()
    }

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. 전략별 백테스팅 실행
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("="*70)
print("💰 전략별 백테스팅 결과 (초기 자본: 100만원)")
print("="*70)

results = []

for strategy in strategies:
    name = strategy['name']
    fast = strategy['fast']
    slow = strategy['slow']
    emoji = strategy['emoji']
    
    print(f"\n{emoji} {name} 전략 (SMA{fast}/{slow}) 백테스팅 중...")
    
    result = backtest_strategy(df, fast, slow)
    result['name'] = name
    result['emoji'] = emoji
    result['fast'] = fast
    result['slow'] = slow
    
    results.append(result)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. 결과 출력
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("\n" + "="*70)
print("📊 백테스팅 결과 요약")
print("="*70)

# 결과를 수익률 순으로 정렬
results_sorted = sorted(results, key=lambda x: x['total_return'], reverse=True)

for i, result in enumerate(results_sorted, 1):
    print(f"\n{i}위: {result['emoji']} {result['name']} 전략 (SMA{result['fast']}/{result['slow']})")
    print("-"*70)
    print(f"💰 최종 자산:       {result['final_value']:>12,.0f}원")
    print(f"📈 총 수익률:       {result['total_return']:>12.2f}%")
    print(f"📉 MDD (최대낙폭):  {result['mdd']:>12.2f}%")
    print(f"📊 샤프 비율:       {result['sharpe_ratio']:>12.2f}")
    print(f"🔄 거래 횟수:       {result['num_trades']:>12}회")
    print(f"🎯 승률:            {result['win_rate']:>12.1f}%")
    
    # 수수료 추정
    estimated_commission = result['num_trades'] * result['initial_cash'] * 0.0005
    print(f"💸 수수료 (추정):   {estimated_commission:>12,.0f}원")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. 비교표
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("\n" + "="*70)
print("📊 전략 비교표")
print("="*70)
print(f"{'전략':<12} {'조합':<10} {'수익률':<10} {'MDD':<10} {'샤프':<8} {'거래':<6}")
print("-"*70)

for result in results_sorted:
    combo = f"SMA{result['fast']}/{result['slow']}"
    print(f"{result['emoji']} {result['name']:<10} {combo:<10} "
          f"{result['total_return']:>7.2f}% {result['mdd']:>7.2f}% "
          f"{result['sharpe_ratio']:>6.2f} {result['num_trades']:>4}회")

print("="*70)

# Buy & Hold와 비교
print(f"\n📌 Buy & Hold (그냥 보유):  {buy_hold_return:+.2f}%")
print(f"📌 최고 전략 초과 수익:     {results_sorted[0]['total_return'] - buy_hold_return:+.2f}%")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7. 시각화
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("\n📈 그래프 생성 중...")

# 한글 폰트 설정 (운영체제별 대응)
import platform
import matplotlib.font_manager as fm

system = platform.system()
if system == 'Windows':
    plt.rcParams['font.family'] = 'Malgun Gothic'
elif system == 'Darwin':  # macOS
    plt.rcParams['font.family'] = 'AppleGothic'
else:  # Linux
    # 시스템에 설치된 한글 폰트 찾기
    fonts = [f.name for f in fm.fontManager.ttflist if 'Nanum' in f.name or 'Malgun' in f.name]
    if fonts:
        plt.rcParams['font.family'] = fonts[0]
    else:
        # 한글 폰트 없으면 영어로 대체
        print("⚠️  한글 폰트를 찾을 수 없습니다. 영어로 표시됩니다.")
        plt.rcParams['font.family'] = 'DejaVu Sans'

plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# 1. 수익률 비교 (막대 그래프)
ax1 = axes[0, 0]
# SMA 조합으로 표시 (예: SMA5/20)
strategies_names = [f"SMA{r['fast']}/{r['slow']}" for r in results_sorted]
returns = [r['total_return'] for r in results_sorted]
colors = ['green' if r > 0 else 'red' for r in returns]

bars = ax1.bar(strategies_names, returns, color=colors, alpha=0.7, edgecolor='black')
ax1.axhline(y=buy_hold_return, color='blue', linestyle='--', linewidth=2, label=f'Buy & Hold ({buy_hold_return:.1f}%)')
ax1.axhline(y=0, color='black', linewidth=1)
ax1.set_title('전략별 총 수익률 비교', fontsize=14, fontweight='bold')
ax1.set_ylabel('수익률 (%)', fontsize=12)
ax1.legend()
ax1.grid(True, alpha=0.3)

# 값 표시
for bar in bars:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.1f}%', ha='center', va='bottom' if height > 0 else 'top', fontsize=10)

# 2. 누적 수익률 (라인 차트)
ax2 = axes[0, 1]
for result in results:
    dates = pd.to_datetime(result['dates'])
    portfolio = np.array(result['portfolio_values'])
    returns_cumulative = (portfolio / result['initial_cash'] - 1) * 100
    # SMA 조합으로 표시
    ax2.plot(dates, returns_cumulative, label=f"SMA{result['fast']}/{result['slow']}", linewidth=2)

# Buy & Hold 추가
buy_hold_values = (df['종가'] / df.iloc[0]['종가'] - 1) * 100
ax2.plot(df['날짜'], buy_hold_values, label='Buy & Hold', linestyle='--', linewidth=2, color='blue')

ax2.set_title('누적 수익률 추이', fontsize=14, fontweight='bold')
ax2.set_ylabel('누적 수익률 (%)', fontsize=12)
ax2.legend(loc='best', fontsize=9)
ax2.grid(True, alpha=0.3)
ax2.axhline(y=0, color='black', linewidth=1)

# 3. 샤프 비율 비교
ax3 = axes[1, 0]
sharpe_ratios = [r['sharpe_ratio'] for r in results_sorted]
colors_sharpe = ['green' if s > 1 else 'orange' if s > 0 else 'red' for s in sharpe_ratios]

bars = ax3.bar(strategies_names, sharpe_ratios, color=colors_sharpe, alpha=0.7, edgecolor='black')
ax3.axhline(y=1, color='blue', linestyle='--', linewidth=2, label='기준값 (1.0)')
ax3.set_title('전략별 샤프 비율 (위험 대비 수익)', fontsize=14, fontweight='bold')
ax3.set_ylabel('샤프 비율', fontsize=12)
ax3.legend()
ax3.grid(True, alpha=0.3)

# 값 표시
for bar in bars:
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.2f}', ha='center', va='bottom' if height > 0 else 'top', fontsize=10)

# 4. MDD vs 수익률 (산점도)
ax4 = axes[1, 1]
mdds = [abs(r['mdd']) for r in results]
returns_scatter = [r['total_return'] for r in results]
names_scatter = [f"SMA{r['fast']}/{r['slow']}" for r in results]

scatter = ax4.scatter(mdds, returns_scatter, s=200, alpha=0.6, c=returns_scatter, cmap='RdYlGn', edgecolors='black')

for i, name in enumerate(names_scatter):
    ax4.annotate(name, (mdds[i], returns_scatter[i]), 
                fontsize=9, ha='center', va='bottom')

ax4.axhline(y=0, color='black', linewidth=1)
ax4.axhline(y=buy_hold_return, color='blue', linestyle='--', linewidth=1, label=f'Buy & Hold ({buy_hold_return:.1f}%)')
ax4.set_title('리스크(MDD) vs 수익률', fontsize=14, fontweight='bold')
ax4.set_xlabel('최대 낙폭 (MDD) %', fontsize=12)
ax4.set_ylabel('총 수익률 (%)', fontsize=12)
ax4.legend()
ax4.grid(True, alpha=0.3)
plt.colorbar(scatter, ax=ax4, label='수익률 (%)')

plt.tight_layout()
plt.savefig('strategy_backtest_results.png', dpi=300, bbox_inches='tight')
print("✅ 그래프 저장: strategy_backtest_results.png")
plt.show()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 8. 최종 추천
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("\n" + "="*70)
print("💡 최종 추천")
print("="*70)

best_return = results_sorted[0]
best_sharpe = max(results, key=lambda x: x['sharpe_ratio'])
best_safe = min([r for r in results if r['total_return'] > 0], key=lambda x: abs(x['mdd']), default=results[0])

print(f"\n🏆 최고 수익률: {best_return['emoji']} {best_return['name']} ({best_return['total_return']:.2f}%)")
print(f"💎 최고 샤프비율: {best_sharpe['emoji']} {best_sharpe['name']} ({best_sharpe['sharpe_ratio']:.2f})")
print(f"🛡️  가장 안전: {best_safe['emoji']} {best_safe['name']} (MDD {best_safe['mdd']:.2f}%)")

print("\n" + "="*70)
print("백테스팅 완료! 🎉")
print("="*70)

