"""
분봉 기반 SMA 골든크로스 전략 백테스팅

1분봉 데이터를 수집하여 5분봉/30분봉 이동평균선을 계산하고
1시간 간격으로 거래 신호를 확인하는 전략
"""

import pandas as pd
import requests
import time
from datetime import datetime, timedelta

from strategy.simple_golden_cross import SimpleGoldenCrossStrategy
from strategy.backtest_engine import BacktestEngine

# 설정 파일 import
import config.sma_minute_config as cfg


def fetch_minute_data(market: str, minutes: int = 1, count: int = 1000):
    """
    Upbit API에서 분봉 데이터 수집
    
    Parameters
    ----------
    market : str
        마켓 코드
    minutes : int
        분봉 단위 (1, 3, 5, 10, 15, 30, 60, 240)
    count : int
        수집할 캔들 개수
    
    Returns
    -------
    pd.DataFrame
        가격 데이터
    """
    url = f"https://api.upbit.com/v1/candles/minutes/{minutes}"
    headers = {"accept": "application/json"}
    
    all_data = []
    last_timestamp = None
    
    print(f"📡 {market} {minutes}분봉 데이터 수집 중...")
    
    while len(all_data) < count:
        params = {
            'market': market,
            'count': min(200, count - len(all_data)),
        }
        
        if last_timestamp:
            params['to'] = last_timestamp
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                break
            
            all_data.extend(data)
            last_timestamp = data[-1]['candle_date_time_utc']
            
            print(f"   수집 완료: {len(all_data)}/{count}개")
            time.sleep(0.1)  # API 요청 제한 방지
            
        except Exception as e:
            print(f"⚠️  데이터 수집 중 오류 발생: {e}")
            break
    
    print(f"✅ 총 {len(all_data)}개 캔들 수집 완료!\n")
    
    df = pd.DataFrame(all_data)
    df['날짜'] = pd.to_datetime(df['candle_date_time_kst'])
    df = df.sort_values('날짜').reset_index(drop=True)
    df['종가'] = df['trade_price']
    df['시가'] = df['opening_price']
    df['고가'] = df['high_price']
    df['저가'] = df['low_price']
    df['거래량'] = df['candle_acc_trade_volume']
    
    return df


def resample_to_minutes(df: pd.DataFrame, minutes: int) -> pd.DataFrame:
    """
    1분봉 데이터를 N분봉으로 리샘플링
    
    Parameters
    ----------
    df : pd.DataFrame
        1분봉 데이터
    minutes : int
        리샘플링할 분봉 단위
    
    Returns
    -------
    pd.DataFrame
        리샘플링된 데이터
    """
    df = df.set_index('날짜')
    
    resampled = pd.DataFrame()
    resampled['종가'] = df['종가'].resample(f'{minutes}T').last()
    resampled['시가'] = df['시가'].resample(f'{minutes}T').first()
    resampled['고가'] = df['고가'].resample(f'{minutes}T').max()
    resampled['저가'] = df['저가'].resample(f'{minutes}T').min()
    resampled['거래량'] = df['거래량'].resample(f'{minutes}T').sum()
    
    resampled = resampled.dropna().reset_index()
    
    return resampled


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
    print("=" * 70)
    print("🚀 분봉 SMA 골든크로스 전략 백테스팅")
    print("=" * 70)
    print()
    
    # 설정 출력
    print("📋 전략 설정:")
    print(f"   - 전략: 분봉 골든크로스 (1분봉 데이터 기반)")
    print(f"   - 이동평균: SMA{cfg.FAST_PERIOD}분/{cfg.SLOW_PERIOD}분")
    print(f"   - 거래 간격: {cfg.TRADE_INTERVAL}분마다 (1시간)")
    print(f"   - 코인: {cfg.MARKET}")
    print(f"   - 초기 자본: {cfg.INITIAL_CASH:,}원")
    print(f"   - 수수료: {cfg.COMMISSION * 100}%")
    print()
    
    # 1분봉 데이터 수집
    df_1min = fetch_minute_data(
        market=cfg.MARKET, 
        minutes=cfg.CANDLE_MINUTES,
        count=cfg.CANDLES_COUNT
    )
    
    print(f"📅 분석 기간: {df_1min.iloc[0]['날짜'].strftime('%Y-%m-%d %H:%M')} ~ {df_1min.iloc[-1]['날짜'].strftime('%Y-%m-%d %H:%M')}")
    print(f"📊 시작 가격: {df_1min.iloc[0]['종가']:,.0f}원")
    print(f"📊 종료 가격: {df_1min.iloc[-1]['종가']:,.0f}원")
    
    # 기간 계산
    time_range = df_1min.iloc[-1]['날짜'] - df_1min.iloc[0]['날짜']
    hours = time_range.total_seconds() / 3600
    print(f"📊 분석 기간: {hours:.1f}시간 ({hours/24:.1f}일)")
    print()
    
    # 전략 생성 (분봉 기준)
    strategy = SimpleGoldenCrossStrategy(
        fast_period=cfg.FAST_PERIOD,
        slow_period=cfg.SLOW_PERIOD
    )
    
    # 신호 생성 (1분봉 데이터로)
    all_signals = strategy.generate_signals(df_1min)
    
    # 1시간 간격으로 필터링
    filtered_signals = filter_hourly_signals(
        df_1min, 
        all_signals, 
        interval_minutes=cfg.TRADE_INTERVAL
    )
    
    # 필터링된 신호 통계
    buy_signals = (filtered_signals['signal'] == 'BUY').sum()
    sell_signals = (filtered_signals['signal'] == 'SELL').sum()
    
    print("=" * 70)
    print("📊 전략 통계")
    print("=" * 70)
    print(f"📈 매수 신호: {buy_signals}회 ({cfg.TRADE_INTERVAL}분 간격)")
    print(f"📉 매도 신호: {sell_signals}회 ({cfg.TRADE_INTERVAL}분 간격)")
    print(f"🔄 총 거래 신호: {buy_signals + sell_signals}회")
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
    print("   - 코인 변경: config/sma_minute_config.py 파일의 MARKET 변수 수정")
    print("   - 이동평균 기간: FAST_PERIOD, SLOW_PERIOD 수정")
    print("   - 거래 간격: TRADE_INTERVAL 수정 (분 단위)")
    print("   - 데이터 양: CANDLES_COUNT 수정")


if __name__ == "__main__":
    main()

