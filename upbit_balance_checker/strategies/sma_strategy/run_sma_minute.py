"""
분봉 SMA 골든크로스 전략

1분봉 데이터로 5분/30분 이동평균선을 계산하고
1시간 간격으로 거래 신호를 확인하는 전략
"""

import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

import pandas as pd
from strategies.sma_strategy.strategy import SMAStrategy
from strategies.sma_strategy.config import SMA_MINUTE_CONFIG
from core.backtest_engine import BacktestEngine
from core.data_fetcher import fetch_minute_data


def filter_hourly_signals(df: pd.DataFrame, signals: pd.DataFrame, interval_minutes: int = 60) -> pd.DataFrame:
    """
    신호를 지정된 간격으로 필터링
    
    Parameters
    ----------
    df : pd.DataFrame
        가격 데이터
    signals : pd.DataFrame
        전체 신호
    interval_minutes : int
        거래 확인 간격 (분 단위)
    
    Returns
    -------
    pd.DataFrame
        필터링된 신호
    """
    df_with_signals = df.copy()
    df_with_signals['signal'] = signals['signal']
    df_with_signals['position'] = signals['position']
    
    # 시간 간격으로 필터링 (정각 기준)
    df_with_signals['hour_mark'] = (
        (df_with_signals['날짜'].dt.hour * 60 + df_with_signals['날짜'].dt.minute) 
        % interval_minutes == 0
    )
    
    # 거래 시점만 유지
    filtered = df_with_signals[df_with_signals['hour_mark']].copy()
    
    # 필터링된 신호 생성
    filtered_signals = pd.DataFrame(index=df.index)
    filtered_signals['signal'] = 'HOLD'
    filtered_signals['position'] = 0
    
    # 거래 시점의 신호만 반영
    for idx in filtered.index:
        filtered_signals.loc[idx, 'signal'] = filtered.loc[idx, 'signal']
        filtered_signals.loc[idx, 'position'] = filtered.loc[idx, 'position']
    
    return filtered_signals


def main():
    """메인 함수"""
    config = SMA_MINUTE_CONFIG
    
    print("=" * 70)
    print(f"🚀 {config['name']}")
    print("=" * 70)
    print()
    
    # 설정 출력
    print("📋 전략 설정:")
    print(f"   - 전략: 분봉 골든크로스 (1분봉 데이터 기반)")
    print(f"   - 이동평균: SMA{config['fast_period']}캔들/{config['slow_period']}캔들")
    print(f"   - 거래 간격: {config['trade_interval']}분마다")
    print(f"   - 코인: {config['market']}")
    print(f"   - 초기 자본: {config['initial_cash']:,}원")
    print(f"   - 수수료: {config['commission'] * 100}%")
    print()
    
    # 1분봉 데이터 수집
    df_1min = fetch_minute_data(
        market=config['market'], 
        minutes=config['candle_minutes'],
        count=config['candles_count']
    )
    
    print(f"📅 분석 기간: {df_1min.iloc[0]['날짜'].strftime('%Y-%m-%d %H:%M')} ~ {df_1min.iloc[-1]['날짜'].strftime('%Y-%m-%d %H:%M')}")
    print(f"📊 시작 가격: {df_1min.iloc[0]['종가']:,.0f}원")
    print(f"📊 종료 가격: {df_1min.iloc[-1]['종가']:,.0f}원")
    
    # 기간 계산
    time_range = df_1min.iloc[-1]['날짜'] - df_1min.iloc[0]['날짜']
    hours = time_range.total_seconds() / 3600
    print(f"📊 분석 기간: {hours:.1f}시간 ({hours/24:.1f}일)")
    print()
    
    # 전략 생성 (캔들 기준 - 5개 캔들 vs 30개 캔들)
    strategy = SMAStrategy(
        fast_period=config['fast_period'],
        slow_period=config['slow_period']
    )
    
    # 신호 생성 (1분봉 데이터로)
    all_signals = strategy.generate_signals(df_1min)
    
    # 거래 간격으로 필터링
    filtered_signals = filter_hourly_signals(
        df_1min, 
        all_signals, 
        interval_minutes=config['trade_interval']
    )
    
    # 필터링된 신호 통계
    buy_signals = (filtered_signals['signal'] == 'BUY').sum()
    sell_signals = (filtered_signals['signal'] == 'SELL').sum()
    
    print("=" * 70)
    print("📊 전략 통계")
    print("=" * 70)
    print(f"📈 매수 신호: {buy_signals}회 ({config['trade_interval']}분 간격)")
    print(f"📉 매도 신호: {sell_signals}회 ({config['trade_interval']}분 간격)")
    print(f"🔄 총 거래 신호: {buy_signals + sell_signals}회")
    print()
    
    # 백테스팅 실행
    print("=" * 70)
    print("💰 백테스팅 실행 중...")
    print("=" * 70)
    print()
    
    engine = BacktestEngine(
        initial_cash=config['initial_cash'],
        commission=config['commission']
    )
    
    result = engine.run(df_1min, filtered_signals)
    
    # 결과 출력
    BacktestEngine.print_results(result)
    
    # 거래 내역
    if result['num_trades'] > 0:
        print("\n📋 거래 내역 (최근 10개):")
        print("-" * 70)
        for trade in result['trades'][-10:]:
            trade_type = "매수" if trade.type == 'BUY' else "매도"
            print(f"{trade.date.strftime('%Y-%m-%d %H:%M')} | {trade_type:>4} | "
                  f"가격: {trade.price:>12,.0f}원 | "
                  f"포트폴리오: {trade.portfolio_value:>12,.0f}원")
    
    # 최종 평가
    print("\n" + "=" * 70)
    print("💡 최종 평가")
    print("=" * 70)
    
    if result['total_return'] > result['buy_hold_return']:
        excess = result['total_return'] - result['buy_hold_return']
        print(f"✅ 전략이 Buy & Hold보다 {excess:.2f}%p 더 수익을 냈습니다!")
    else:
        deficit = result['buy_hold_return'] - result['total_return']
        print(f"⚠️  전략이 Buy & Hold보다 {deficit:.2f}%p 적게 수익을 냈습니다.")
    
    if result['sharpe_ratio'] > 1:
        print(f"✅ 샤프 비율 {result['sharpe_ratio']:.2f}: 위험 대비 수익이 좋습니다!")
    elif result['sharpe_ratio'] > 0:
        print(f"⚠️  샤프 비율 {result['sharpe_ratio']:.2f}: 보통 수준입니다.")
    else:
        print(f"❌ 샤프 비율 {result['sharpe_ratio']:.2f}: 위험 대비 수익이 낮습니다.")
    
    print("=" * 70)
    print("\n💡 설정 변경:")
    print("   - 코인 변경: strategies/sma_strategy/config.py의 SMA_MINUTE_CONFIG 수정")
    print("   - 이동평균 기간: fast_period, slow_period 수정")
    print("   - 거래 간격: trade_interval 수정 (분 단위)")
    print("   - 데이터 양: candles_count 수정")
    print("\n⚠️  참고: 이 전략은 5개 캔들 vs 30개 캔들의 이동평균을 비교합니다.")
    print("         (진짜 5분봉 vs 30분봉이 아니라, 1분봉 5개 vs 1분봉 30개)")


if __name__ == "__main__":
    main()










