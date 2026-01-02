"""
골든크로스 + RSI 필터 전략 백테스팅 실행

설정 파일(config/goldcross_rsi_config.py)의 값을 변경하여 전략을 조정할 수 있습니다.
"""

import sys
from pathlib import Path
import pandas as pd
import requests
import time
from datetime import datetime

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from strategies.goldcross_rsi_strategy.strategy import GoldenCrossRSIStrategy
from core.backtest_engine import BacktestEngine
from core.data_fetcher import fetch_daily_data, fetch_minute_data
from strategies.goldcross_rsi_strategy import config as cfg
from global_config import get_timeframe, get_candles_count




def main():
    """메인 함수"""
    print("=" * 70)
    print("🚀 골든크로스 + RSI 필터 전략 백테스팅")
    print("=" * 70)
    print()
    
    # 설정 출력
    print("📋 전략 설정:")
    print(f"   - 이동평균: SMA{cfg.FAST_PERIOD}/{cfg.SLOW_PERIOD}")
    print(f"   - RSI 기간: {cfg.RSI_PERIOD}")
    print(f"   - RSI 매수 필터: {cfg.RSI_BUY_THRESHOLD} 이하")
    print(f"   - RSI 매도 필터: {cfg.RSI_SELL_THRESHOLD} 이상")
    print(f"   - 초기 자본: {cfg.INITIAL_CASH:,}원")
    print(f"   - 수수료: {cfg.COMMISSION * 100}%")
    print()
    
    # 데이터 수집 (global_config에서 시간 단위 가져오기)
    timeframe = get_timeframe('goldcross_rsi')
    
    if timeframe['type'] == 'daily':
        df = fetch_daily_data(
            market=cfg.MARKET,
            days=get_candles_count('daily')
        )
    else:
        df = fetch_minute_data(
            market=cfg.MARKET,
            minutes=timeframe['minutes'],
            count=get_candles_count('minutes')
        )
    
    print(f"📅 분석 기간: {df.index[0].strftime('%Y-%m-%d')} ~ {df.index[-1].strftime('%Y-%m-%d')}")
    print(f"📊 시작 가격: {df.iloc[0]['종가']:,.0f}원")
    print(f"📊 종료 가격: {df.iloc[-1]['종가']:,.0f}원")
    print()
    
    # 전략 생성
    strategy = GoldenCrossRSIStrategy(
        fast_period=cfg.FAST_PERIOD,
        slow_period=cfg.SLOW_PERIOD,
        rsi_period=cfg.RSI_PERIOD,
        rsi_buy_threshold=cfg.RSI_BUY_THRESHOLD,
        rsi_sell_threshold=cfg.RSI_SELL_THRESHOLD
    )
    
    # 전략 통계
    stats = strategy.get_statistics(df)
    print("=" * 70)
    print("📊 전략 통계")
    print("=" * 70)
    print(f"📈 골든크로스: {stats['golden_cross_count']}회")
    print(f"📉 데드크로스: {stats['dead_cross_count']}회")
    print(f"🔄 총 크로스: {stats['total_crosses']}회")
    print(f"🚫 RSI 필터로 취소된 매수: {stats['filtered_buys']}회")
    print(f"🚫 RSI 필터로 취소된 매도: {stats['filtered_sells']}회")
    print()
    
    # 백테스팅 실행
    print("=" * 70)
    print("💰 백테스팅 실행 중...")
    print("=" * 70)
    print()
    
    engine = BacktestEngine(
        initial_cash=cfg.INITIAL_CASH,
        commission=cfg.COMMISSION
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
    print("\n💡 설정 변경: config/goldcross_rsi_config.py 파일을 수정하여 전략을 조정할 수 있습니다.")


if __name__ == "__main__":
    main()

