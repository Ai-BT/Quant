"""
MACD + Trend Filter 전략 백테스팅 (1시간 체크 시뮬레이션)

일봉 기준 전략이지만, 1시간마다 체크하면서 신호 변화를 감지하는 백테스트

Usage:
    python run_macd_hourly_check.py
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# ============================================================================
# 여기서 사용할 설정 선택
# ============================================================================
from strategies.macd_strategy.config import MACD_TREND_CONFIG as cfg

from core.data_fetcher import fetch_daily_data
from core.logger import save_results_to_file
from strategies.macd_strategy.strategy import MACDTrendStrategy


def print_separator(char="=", length=70):
    """구분선 출력"""
    print(char * length)


def simulate_hourly_check_backtest(df_daily, strategy, initial_cash=1_000_000, commission=0.0005):
    """
    1시간마다 체크하는 백테스팅 시뮬레이션
    
    Args:
        df_daily: 일봉 데이터
        strategy: MACD 전략
        initial_cash: 초기 자본
        commission: 수수료율
    
    Returns:
        dict: 백테스팅 결과
    """
    
    # 초기 설정
    cash = initial_cash
    position = 0  # 보유 수량
    trades = []
    portfolio_values = []
    
    previous_signal = 'HOLD'
    entry_price = 0
    
    print("\n🔍 1시간 체크 백테스팅 시작...")
    print_separator("-")
    
    # 일봉 데이터를 순회하면서 1시간마다 체크하는 것을 시뮬레이션
    for i in range(len(df_daily)):
        # 현재 시점까지의 데이터로 신호 생성
        df_current = df_daily.iloc[:i+1].copy()
        
        if len(df_current) < strategy.trend_ma_period:
            # 데이터가 충분하지 않으면 스킵
            continue
        
        # 신호 생성
        signals = strategy.generate_signals(df_current)
        current_signal = signals.iloc[-1]['signal']
        current_price = df_current.iloc[-1]['종가']
        current_date = df_current.index[-1]
        
        # 1시간마다 체크하는 것을 시뮬레이션 (하루에 24번 체크)
        # 실제로는 일봉이므로 하루에 1번만 가격이 업데이트되지만,
        # 신호가 바뀌는 시점을 포착하는 것을 시뮬레이션
        
        # 신호 변화 감지
        if current_signal != previous_signal:
            
            # 매수 신호
            if current_signal == 'BUY' and position == 0:
                # 전액 매수
                buy_amount = cash * (1 - commission)
                position = buy_amount / current_price
                entry_price = current_price
                
                trades.append({
                    'date': current_date,
                    'type': 'BUY',
                    'price': current_price,
                    'quantity': position,
                    'cash_before': cash,
                    'cash_after': 0,
                    'portfolio_value': position * current_price
                })
                
                cash = 0
                print(f"[{current_date.strftime('%Y-%m-%d')}] 매수 🟢 | 가격: {current_price:,.0f}원 | 수량: {position:.8f}")
            
            # 매도 신호
            elif current_signal == 'SELL' and position > 0:
                # 전량 매도
                sell_amount = position * current_price * (1 - commission)
                profit = sell_amount - initial_cash
                profit_rate = (sell_amount / initial_cash - 1) * 100
                
                trades.append({
                    'date': current_date,
                    'type': 'SELL',
                    'price': current_price,
                    'quantity': position,
                    'cash_before': 0,
                    'cash_after': sell_amount,
                    'portfolio_value': sell_amount,
                    'profit': profit,
                    'profit_rate': profit_rate
                })
                
                cash = sell_amount
                position = 0
                print(f"[{current_date.strftime('%Y-%m-%d')}] 매도 🔴 | 가격: {current_price:,.0f}원 | 수익률: {profit_rate:+.2f}%")
        
        previous_signal = current_signal
        
        # 포트폴리오 가치 기록
        if position > 0:
            portfolio_value = position * current_price
        else:
            portfolio_value = cash
        
        portfolio_values.append({
            'date': current_date,
            'value': portfolio_value,
            'signal': current_signal
        })
    
    # 최종 청산 (포지션이 남아있으면)
    if position > 0:
        final_price = df_daily.iloc[-1]['종가']
        final_value = position * final_price * (1 - commission)
        final_date = df_daily.index[-1]
        
        profit = final_value - initial_cash
        profit_rate = (final_value / initial_cash - 1) * 100
        
        trades.append({
            'date': final_date,
            'type': 'SELL',
            'price': final_price,
            'quantity': position,
            'cash_before': 0,
            'cash_after': final_value,
            'portfolio_value': final_value,
            'profit': profit,
            'profit_rate': profit_rate
        })
        
        cash = final_value
        position = 0
        print(f"[{final_date.strftime('%Y-%m-%d')}] 최종 청산 🔴 | 가격: {final_price:,.0f}원 | 수익률: {profit_rate:+.2f}%")
    
    # 최종 자산
    final_value = cash if position == 0 else position * df_daily.iloc[-1]['종가']
    
    # Buy & Hold 수익률
    buy_hold_return = (df_daily.iloc[-1]['종가'] / df_daily.iloc[0]['종가'] - 1) * 100
    
    # 수익률 계산
    total_return = (final_value / initial_cash - 1) * 100
    net_profit = final_value - initial_cash
    
    # MDD 계산
    portfolio_df = pd.DataFrame(portfolio_values)
    portfolio_df['peak'] = portfolio_df['value'].cummax()
    portfolio_df['drawdown'] = (portfolio_df['value'] / portfolio_df['peak'] - 1) * 100
    mdd = portfolio_df['drawdown'].min()
    
    # 승률 계산
    winning_trades = [t for t in trades if t['type'] == 'SELL' and t.get('profit', 0) > 0]
    total_trades = len([t for t in trades if t['type'] == 'SELL'])
    win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0
    
    # Sharpe Ratio 계산
    if len(portfolio_df) > 1:
        portfolio_df['returns'] = portfolio_df['value'].pct_change()
        sharpe_ratio = portfolio_df['returns'].mean() / portfolio_df['returns'].std() * (252 ** 0.5) if portfolio_df['returns'].std() > 0 else 0
    else:
        sharpe_ratio = 0
    
    print_separator("-")
    print(f"✅ 백테스팅 완료 | 총 거래: {total_trades}회\n")
    
    return {
        'initial_cash': initial_cash,
        'final_value': final_value,
        'net_profit': net_profit,
        'total_return': total_return,
        'buy_hold_return': buy_hold_return,
        'mdd': mdd,
        'sharpe_ratio': sharpe_ratio,
        'num_trades': total_trades,
        'win_rate': win_rate,
        'trades': trades,
        'portfolio_values': portfolio_df
    }


def main():
    """메인 실행 함수"""
    
    config = cfg
    
    print("\n" + "🚀 " * 35)
    print_separator()
    print(f"  MACD + Trend Filter 전략 백테스팅 (1시간 체크)")
    print_separator()
    print()
    
    # 설정 출력
    print("📋 전략 설정")
    print_separator("-")
    print(f"전략 이름      : {config['name']} (1시간 체크)")
    print(f"마켓          : {config['market']}")
    print(f"초기 자본      : {config['initial_cash']:,}원")
    print(f"수수료        : {config['commission']*100}%")
    print(f"체크 주기      : 1시간 (시뮬레이션)")
    print()
    
    print("📊 MACD 설정")
    print_separator("-")
    print(f"Fast Period   : {config['macd_fast']}일 EMA")
    print(f"Slow Period   : {config['macd_slow']}일 EMA")
    print(f"Signal Period : {config['macd_signal']}일 EMA")
    print()
    
    print("🎯 Trend Filter 설정")
    print_separator("-")
    print(f"Trend MA      : {config['trend_ma_period']}일 {config['trend_ma_type']}")
    if config.get('use_histogram_filter', False):
        print(f"Histogram Filter: ✅ 활성화 (최소값: {config.get('min_histogram', 0)})")
    print()
    
    print("⏰ 백테스팅 방식")
    print_separator("-")
    print("📌 일봉 기준 MACD 계산")
    print("📌 1시간마다 신호 체크 시뮬레이션")
    print("📌 신호 변화 시 즉시 매매")
    print()
    
    # 데이터 가져오기
    print("📥 데이터 로딩 중...")
    df = fetch_daily_data(
        market=config['market'],
        days=config['candles_count']
    )
    print(f"✅ 데이터 로딩 완료: {len(df)}개 캔들 (일봉)")
    print(f"   기간: {df.index[0].strftime('%Y-%m-%d')} ~ {df.index[-1].strftime('%Y-%m-%d')}")
    print()
    
    # 전략 생성
    strategy = MACDTrendStrategy(
        macd_fast=config['macd_fast'],
        macd_slow=config['macd_slow'],
        macd_signal=config['macd_signal'],
        trend_ma_period=config['trend_ma_period'],
        trend_ma_type=config['trend_ma_type'],
        use_trend_filter=config.get('use_trend_filter', True),
        use_histogram_filter=config.get('use_histogram_filter', False),
        min_histogram=config.get('min_histogram', 0),
    )
    
    # 1시간 체크 백테스팅 실행
    result = simulate_hourly_check_backtest(
        df_daily=df,
        strategy=strategy,
        initial_cash=config['initial_cash'],
        commission=config['commission']
    )
    
    # 결과 출력
    print_separator("=")
    print("📊 백테스팅 결과")
    print_separator("=")
    print()
    
    # 수익률 결과
    print("💰 수익률 분석")
    print_separator("-")
    print(f"초기 자본       : {result['initial_cash']:>15,.0f}원")
    print(f"최종 자산       : {result['final_value']:>15,.0f}원")
    print(f"순이익         : {result['net_profit']:>15,.0f}원")
    print(f"총 수익률       : {result['total_return']:>14.2f}%")
    print(f"Buy&Hold 수익률 : {result['buy_hold_return']:>14.2f}%")
    print(f"초과 수익       : {result['total_return'] - result['buy_hold_return']:>14.2f}%p")
    print()
    
    # 리스크 지표
    print("📉 리스크 지표")
    print_separator("-")
    print(f"MDD (최대 낙폭) : {result['mdd']:>14.2f}%")
    print(f"Sharpe Ratio    : {result['sharpe_ratio']:>14.2f}")
    print()
    
    # 거래 통계
    print("📈 거래 통계")
    print_separator("-")
    print(f"총 거래 횟수    : {result['num_trades']:>14}회")
    print(f"승률           : {result['win_rate']:>14.2f}%")
    print()
    
    # 최근 거래 내역
    if result['num_trades'] > 0:
        print_separator("=")
        print(f"📋 거래 내역 (총 {result['num_trades']}건)")
        print_separator("=")
        print()
        print(f"{'번호':<6} {'날짜':<12} {'유형':<6} {'가격':>15} {'수익률':>10}")
        print_separator("-")
        
        trade_num = 0
        for trade in result['trades']:
            if trade['type'] == 'SELL':
                trade_num += 1
                trade_type = "매도 🔴"
                profit_rate = trade.get('profit_rate', 0)
                print(f"{trade_num:<6} {trade['date'].strftime('%Y-%m-%d'):<12} {trade_type:<6} "
                      f"{trade['price']:>15,.0f}원 {profit_rate:>9.2f}%")
        print()
    
    print_separator("=")
    print()
    
    # 결과 파일 저장
    stats = {
        'macd_fast': config['macd_fast'],
        'macd_slow': config['macd_slow'],
        'macd_signal': config['macd_signal'],
        'trend_ma_period': config['trend_ma_period'],
        'use_trend_filter': True,
        'use_histogram_filter': config.get('use_histogram_filter', False),
        'check_interval': '1시간 (시뮬레이션)',
        'total_signals': len([t for t in result['trades'] if t['type'] == 'BUY']),
        'buy_signals': len([t for t in result['trades'] if t['type'] == 'BUY']),
        'sell_signals': len([t for t in result['trades'] if t['type'] == 'SELL']),
    }
    
    # config에 체크 방식 추가
    config_with_check = config.copy()
    config_with_check['name'] = config['name'] + '_Hourly_Check'
    
    save_results_to_file(result, config_with_check, stats, output_dir="results")
    
    print(f"📄 결과 파일 저장 완료!")
    
    print()
    print("✅ 백테스팅 완료!")
    print("📌 일봉 기준 전략 + 1시간 체크 시뮬레이션")
    print()


if __name__ == "__main__":
    main()

