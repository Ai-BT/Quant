"""
MACD + Trend Filter 전략 백테스팅 실행

Usage:
    python run_macd.py
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# ============================================================================
# 여기서 사용할 설정 선택 (auto-import 정리 방지용 주석 포함)
# ============================================================================
# from strategies.macd_strategy.config import MACD_TREND_CONFIG as cfg      # 일봉 
from strategies.macd_strategy.config import MACD_TREND_CONFIG as cfg      # 15분봉
# from strategies.macd_strategy.config import MACD_1MIN_CONFIG as cfg        # 1분봉

from core.backtest_engine import BacktestEngine
from core.data_fetcher import fetch_daily_data, fetch_minute_data
from core.logger import save_results_to_file
from strategies.macd_strategy.strategy import MACDTrendStrategy  


def print_separator(char="=", length=70):
    """구분선 출력"""
    print(char * length)


def main():
    """메인 실행 함수"""

    config = cfg

    print("\n" + "🚀 " * 35)
    print_separator()
    print(f"  MACD + Trend Filter 전략 백테스팅")
    print_separator()
    print()

    # 설정 출력
    print("📋 전략 설정")
    print_separator("-")
    print(f"전략 이름      : {config['name']}")
    print(f"마켓          : {config['market']}")
    print(f"초기 자본      : {config['initial_cash']:,}원")
    print(f"수수료        : {config['commission']*100}%")
    print()

    print("📊 MACD 설정")
    print_separator("-")
    print(f"Fast Period   : {config['macd_fast']}일 EMA")
    print(f"Slow Period   : {config['macd_slow']}일 EMA")
    print(f"Signal Period : {config['macd_signal']}일 EMA")
    print()

    print("🎯 Trend Filter 설정")
    print_separator("-")
    use_trend = config.get('use_trend_filter', True)
    if use_trend:
        print(f"Trend MA      : {config['trend_ma_period']}일 {config['trend_ma_type']}")
        if config.get('use_dual_trend', False):
            print(f"Mid Trend MA  : {config.get('mid_trend_period', 50)}일 {config['trend_ma_type']}")
            print("📌 이중 트렌드 필터 활성화")
    else:
        print("Trend Filter  : ❌ 비활성화")
    print()

    if config.get('use_histogram_filter', False):
        print("📈 Histogram Filter 활성화")
        print(f"   최소값: {config.get('min_histogram', 0)}")
        print()

    if config.get('use_volume_filter', False):
        print("📊 Volume Filter 활성화")
        print(f"   거래량 MA: {config.get('volume_ma_period', 20)}일")
        print(f"   최소 배수: {config.get('volume_multiplier', 1.2)}배")
        print()

    # 데이터 가져오기
    print("📥 데이터 로딩 중...")

    timeframe = config.get('timeframe', 'daily')

    if timeframe == 'minute':
        # 분봉 데이터
        candle_minutes = config.get('candle_minutes', 1)
        df = fetch_minute_data(
            market=config['market'],
            minutes=candle_minutes,
            count=config['candles_count']
        )
        print(f"✅ 데이터 로딩 완료: {len(df)}개 캔들 ({candle_minutes}분봉)")
    else:
        # 일봉 데이터
        df = fetch_daily_data(
            market=config['market'],
            days=config['candles_count']
        )
        print(f"✅ 데이터 로딩 완료: {len(df)}개 캔들 (일봉)")

    print(f"   기간: {df.index[0]} ~ {df.index[-1]}")
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
        use_dual_trend=config.get('use_dual_trend', False),
        mid_trend_period=config.get('mid_trend_period', 50),
        use_volume_filter=config.get('use_volume_filter', False),
        volume_ma_period=config.get('volume_ma_period', 20),
        volume_multiplier=config.get('volume_multiplier', 1.2),
    )

    # 신호 생성
    print("🔍 매매 신호 생성 중...")
    signals = strategy.generate_signals(df)

    # 전략 통계
    stats = strategy.get_statistics(df, signals)
    print(f"✅ 신호 생성 완료")
    print(f"   총 신호: {stats['total_signals']}개")
    print(f"   매수 신호: {stats['buy_signals']}개")
    print(f"   매도 신호: {stats['sell_signals']}개")
    print()

    # 백테스팅 실행
    print("🎮 백테스팅 실행 중...")
    print_separator("-")

    engine = BacktestEngine(
        initial_cash=config['initial_cash'],
        commission=config['commission']
    )

    result = engine.run(df, signals)

    print()
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

    # 전략 파라미터
    print("⚙️  전략 파라미터")
    print_separator("-")
    print(f"MACD Fast       : {stats['macd_fast']:>14}일")
    print(f"MACD Slow       : {stats['macd_slow']:>14}일")
    print(f"MACD Signal     : {stats['macd_signal']:>14}일")
    if stats['use_trend_filter']:
        print(f"Trend MA        : {stats['trend_ma_period']:>14}일")
    if stats['use_dual_trend']:
        print(f"📌 이중 트렌드 필터 사용")
    if stats['use_histogram_filter']:
        print(f"📈 Histogram 필터 사용")
    if stats['use_volume_filter']:
        print(f"📊 Volume 필터 사용")
    print()

    # 최근 거래 내역 (최근 10건)
    if result['num_trades'] > 0:
        print_separator("=")
        print(f"📋 최근 거래 내역 (최근 10건 / 총 {result['num_trades']}건)")
        print_separator("=")
        print()
        print(f"{'번호':<6} {'날짜':<12} {'유형':<6} {'가격':>15} {'수량':>12} {'포트폴리오':>15}")
        print_separator("-")

        recent_trades = result['trades'][-10:]
        for i, trade in enumerate(recent_trades, 1):
            trade_type = "매수 🟢" if trade.type == 'BUY' else "매도 🔴"
            print(f"{i:<6} {trade.date.strftime('%Y-%m-%d'):<12} {trade_type:<6} "
                  f"{trade.price:>15,.0f}원 {trade.quantity:>12.8f} {trade.portfolio_value:>15,.0f}원")
        print()

    print_separator("=")
    print()

    # 결과 파일 저장
    save_results_to_file(result, config, stats, output_dir="results")

    print()
    print("✅ 백테스팅 완료!")
    print()


if __name__ == "__main__":
    main()
