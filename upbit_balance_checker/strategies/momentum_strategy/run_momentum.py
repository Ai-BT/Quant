"""
모멘텀 전략 실행

일봉 데이터를 사용한 모멘텀 전략 (기본 20일)
"""

import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

import pandas as pd
from strategies.momentum_strategy.strategy import MomentumStrategy
from strategies.momentum_strategy.config import MOMENTUM_20_CONFIG
from core.backtest_engine import BacktestEngine
from core.data_fetcher import fetch_daily_data
from core.logger import setup_logger, save_results_to_file, save_trades_to_csv


def main():
    """메인 함수"""
    config = MOMENTUM_20_CONFIG
    
    # 로거 설정 (화면 + 파일 동시 출력)
    logger = setup_logger(
        strategy_name=config['name'],
        market=config['market'],
        output_dir="logs"
    )
    sys.stdout = logger
    
    print("=" * 70)
    print(f"🚀 {config['name']}")
    print("=" * 70)
    print()
    
    # 설정 출력
    print("📋 전략 설정:")
    print(f"   - 모멘텀 기간: {config['lookback_period']}일")
    print(f"   - 매수 기준: {config['buy_threshold']*100:+.1f}% 이상")
    print(f"   - 매도 기준: {config['sell_threshold']*100:+.1f}% 이하")
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
    
    # 전체 수익률
    total_return = (df.iloc[-1]['종가'] / df.iloc[0]['종가'] - 1) * 100
    print(f"📊 기간 수익률: {total_return:+.2f}%")
    print()
    
    # 전략 생성
    strategy = MomentumStrategy(
        lookback_period=config['lookback_period'],
        buy_threshold=config['buy_threshold'],
        sell_threshold=config['sell_threshold']
    )
    
    # 전략 통계
    stats = strategy.get_statistics(df)
    print("=" * 70)
    print("📊 전략 통계")
    print("=" * 70)
    print(f"📈 매수 신호: {stats['buy_signals']}회")
    print(f"📉 매도 신호: {stats['sell_signals']}회")
    print(f"🔄 총 신호: {stats['total_signals']}회")
    print()
    print("📊 모멘텀 분석:")
    print(f"   - 평균 모멘텀: {stats['avg_momentum']*100:+.2f}%")
    print(f"   - 최대 모멘텀: {stats['max_momentum']*100:+.2f}%")
    print(f"   - 최소 모멘텀: {stats['min_momentum']*100:+.2f}%")
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
            # 해당 날짜의 모멘텀 찾기
            idx = df[df['날짜'] == trade.date].index
            if len(idx) > 0 and idx[0] in signals.index:
                momentum = signals.loc[idx[0], 'momentum']
                momentum_str = f"모멘텀: {momentum*100:+6.2f}%" if pd.notna(momentum) else "모멘텀: N/A"
            else:
                momentum_str = "모멘텀: N/A"
            
            print(f"{trade.date.strftime('%Y-%m-%d')} | {trade_type:>4} | "
                  f"가격: {trade.price:>12,.0f}원 | {momentum_str} | "
                  f"포트폴리오: {trade.portfolio_value:>12,.0f}원")
    
    # 최종 평가
    print("\n" + "=" * 70)
    print("💡 최종 평가")
    print("=" * 70)
    
    excess = result['total_return'] - result['buy_hold_return']
    
    if result['total_return'] > result['buy_hold_return']:
        if result['total_return'] > 0 and result['buy_hold_return'] > 0:
            # 둘 다 수익
            print(f"✅ 전략이 Buy & Hold보다 {excess:.2f}%p 더 수익을 냈습니다!")
        elif result['total_return'] > 0 and result['buy_hold_return'] < 0:
            # 전략은 수익, Buy & Hold는 손실
            print(f"✅ 전략이 수익({result['total_return']:.2f}%)을 냈고, Buy & Hold({result['buy_hold_return']:.2f}%)보다 {excess:.2f}%p 더 좋습니다!")
        else:
            # 둘 다 손실이지만 전략이 덜 손실
            print(f"✅ 전략이 Buy & Hold보다 {excess:.2f}%p 덜 손실을 냈습니다! (전략: {result['total_return']:.2f}%, Buy & Hold: {result['buy_hold_return']:.2f}%)")
    else:
        deficit = -excess
        if result['total_return'] < 0 and result['buy_hold_return'] < 0:
            # 둘 다 손실이지만 전략이 더 손실
            print(f"⚠️  전략이 Buy & Hold보다 {deficit:.2f}%p 더 손실을 냈습니다. (전략: {result['total_return']:.2f}%, Buy & Hold: {result['buy_hold_return']:.2f}%)")
        else:
            print(f"⚠️  전략이 Buy & Hold보다 {deficit:.2f}%p 적게 수익을 냈습니다.")
    
    if result['sharpe_ratio'] > 1:
        print(f"✅ 샤프 비율 {result['sharpe_ratio']:.2f}: 위험 대비 수익이 좋습니다!")
    elif result['sharpe_ratio'] > 0:
        print(f"⚠️  샤프 비율 {result['sharpe_ratio']:.2f}: 보통 수준입니다.")
    else:
        print(f"❌ 샤프 비율 {result['sharpe_ratio']:.2f}: 위험 대비 수익이 낮습니다.")
    
    print("=" * 70)
    print("\n💡 설정 변경: strategies/momentum_strategy/config.py의 MOMENTUM_20_CONFIG 수정")
    print("\n📚 모멘텀 전략 설명:")
    print(f"   - {config['lookback_period']}일 전 가격과 현재 가격을 비교")
    print(f"   - 수익률이 {config['buy_threshold']*100:+.1f}% 이상이면 매수")
    print(f"   - 수익률이 {config['sell_threshold']*100:+.1f}% 이하면 매도")
    print("   - 상승 추세를 따라가는 추세 추종 전략")
    
    # 결과 파일 저장
    print("\n" + "=" * 70)
    print("💾 결과 저장 중...")
    print("=" * 70)
    save_results_to_file(result, config, stats, output_dir="results")
    save_trades_to_csv(result, config, output_dir="results")
    print("✅ 저장 완료!")
    
    # 로거 종료
    logger.close()
    sys.stdout = logger.terminal


if __name__ == "__main__":
    main()

