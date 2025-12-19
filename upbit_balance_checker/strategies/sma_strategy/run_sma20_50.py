"""
SMA 20/50 골든크로스 전략 실행

일봉 데이터를 사용한 SMA 20/50 전략
"""

import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

import pandas as pd
from strategies.sma_strategy.strategy import SMAStrategy
from strategies.sma_strategy.config import SMA20_50_CONFIG
from core.backtest_engine import BacktestEngine
from core.data_fetcher import fetch_daily_data


def main():
    """메인 함수"""
    config = SMA20_50_CONFIG
    
    print("=" * 70)
    print(f"🚀 {config['name']}")
    print("=" * 70)
    print()
    
    # 설정 출력
    print("📋 전략 설정:")
    print(f"   - 이동평균: SMA{config['fast_period']}/{config['slow_period']}")
    print(f"   - 코인: {config['market']}")
    print(f"   - 초기 자본: {config['initial_cash']:,}원")
    print(f"   - 수수료: {config['commission'] * 100}%")
    print()
    
    # 데이터 수집
    df = fetch_daily_data(
        market=config['market'],
        days=config['candles_count']
    )
    
    print(f"📅 분석 기간: {df.iloc[0]['날짜'].strftime('%Y-%m-%d')} ~ {df.iloc[-1]['날짜'].strftime('%Y-%m-%d')}")
    print(f"📊 시작 가격: {df.iloc[0]['종가']:,.0f}원")
    print(f"📊 종료 가격: {df.iloc[-1]['종가']:,.0f}원")
    print()
    
    # 전략 생성
    strategy = SMAStrategy(
        fast_period=config['fast_period'],
        slow_period=config['slow_period']
    )
    
    # 전략 통계
    stats = strategy.get_statistics(df)
    print("=" * 70)
    print("📊 전략 통계")
    print("=" * 70)
    print(f"📈 골든크로스: {stats['golden_cross_count']}회")
    print(f"📉 데드크로스: {stats['dead_cross_count']}회")
    print(f"🔄 총 크로스: {stats['total_crosses']}회")
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
    
    signals = strategy.generate_signals(df)
    result = engine.run(df, signals)
    
    # 결과 출력
    BacktestEngine.print_results(result)
    
    # 거래 내역
    if result['num_trades'] > 0:
        print("\n📋 거래 내역 (최근 10개):")
        print("-" * 70)
        for trade in result['trades'][-10:]:
            trade_type = "매수" if trade.type == 'BUY' else "매도"
            print(f"{trade.date.strftime('%Y-%m-%d')} | {trade_type:>4} | "
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
    print("\n💡 설정 변경: strategies/sma_strategy/config.py의 SMA20_50_CONFIG 수정")


if __name__ == "__main__":
    main()





