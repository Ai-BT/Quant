"""
MACD 실시간 가상 거래 봇 실행

MACD + Trend Filter 전략을 사용한 24시간 실시간 거래 시뮬레이션
"""

import time
import signal
import sys
from datetime import datetime

from config_macd import (
    MARKET, INTERVAL, CANDLE_MINUTES, CANDLE_COUNT,
    INITIAL_CASH, COMMISSION,
    MACD_FAST, MACD_SLOW, MACD_SIGNAL,
    TREND_MA_PERIOD, TREND_MA_TYPE,
    USE_TREND_FILTER, USE_HISTOGRAM_FILTER, MIN_HISTOGRAM,
    USE_DUAL_TREND, MID_TREND_PERIOD,
    USE_VOLUME_FILTER, VOLUME_MA_PERIOD, VOLUME_MULTIPLIER,
    LOG_DIR, SAVE_TRADES
)
from realtime_data import RealtimeDataFetcher
from paper_trading_engine import PaperTradingEngine
from macd_strategy import MACDRealtimeStrategy
from logger import TradingLogger, print_header


class MACDRealtimeTradingBot:
    """MACD 실시간 거래 봇 클래스"""

    def __init__(self):
        """봇 초기화"""
        # 데이터 수집기
        self.data_fetcher = RealtimeDataFetcher(
            market=MARKET,
            candle_minutes=CANDLE_MINUTES
        )

        # 거래 엔진
        self.engine = PaperTradingEngine(
            initial_cash=INITIAL_CASH,
            commission=COMMISSION
        )

        # 전략
        self.strategy = MACDRealtimeStrategy(
            macd_fast=MACD_FAST,
            macd_slow=MACD_SLOW,
            macd_signal=MACD_SIGNAL,
            trend_ma_period=TREND_MA_PERIOD,
            trend_ma_type=TREND_MA_TYPE,
            use_trend_filter=USE_TREND_FILTER,
            use_histogram_filter=USE_HISTOGRAM_FILTER,
            min_histogram=MIN_HISTOGRAM,
            use_dual_trend=USE_DUAL_TREND,
            mid_trend_period=MID_TREND_PERIOD,
            use_volume_filter=USE_VOLUME_FILTER,
            volume_ma_period=VOLUME_MA_PERIOD,
            volume_multiplier=VOLUME_MULTIPLIER
        )

        # 로거
        self.logger = TradingLogger(log_dir=LOG_DIR, market=MARKET)

        # 봇 실행 상태
        self.running = True

        # 시그널 핸들러 등록 (Ctrl+C로 종료)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, sig, frame):
        """시그널 핸들러 (Ctrl+C 처리)"""
        print("\n\n봇을 종료합니다...")
        self.running = False

    def run(self):
        """봇 실행"""
        # 헤더 출력
        print_header(MARKET, self.strategy.name)
        self.logger.info(f"MACD 실시간 거래 봇 시작 - {MARKET}")
        self.logger.info(f"전략: {self.strategy.name}")
        self.logger.info(f"초기 자본: {INITIAL_CASH:,}원")
        self.logger.info(f"체크 주기: {INTERVAL}초")
        self.logger.info(f"Trend Filter: {'사용' if USE_TREND_FILTER else '미사용'}")
        if USE_TREND_FILTER:
            self.logger.info(f"  - Trend MA: {TREND_MA_PERIOD}일 {TREND_MA_TYPE}")
            if USE_DUAL_TREND:
                self.logger.info(f"  - Mid Trend MA: {MID_TREND_PERIOD}일 {TREND_MA_TYPE}")

        while self.running:
            try:
                # 1. 데이터 수집
                df = self.data_fetcher.fetch_latest_candles(count=CANDLE_COUNT)

                if df is None or len(df) == 0:
                    self.logger.warning("데이터 수집 실패")
                    time.sleep(INTERVAL)
                    continue

                # 2. 전략 분석
                analysis = self.strategy.analyze(df)

                # 3. 현재 가격
                current_price = analysis.get('price', 0)

                if current_price == 0:
                    self.logger.warning("현재 가격 정보 없음")
                    time.sleep(INTERVAL)
                    continue

                # 4. 거래 실행
                timestamp = datetime.now()

                if analysis['signal'] == 'BUY' and self.engine.position == 0:
                    # 매수
                    success = self.engine.buy(
                        price=current_price,
                        timestamp=timestamp,
                        reason=analysis['reason']
                    )

                    if success:
                        self.logger.log_trade(
                            trade_type='BUY',
                            price=current_price,
                            quantity=self.engine.position,
                            reason=analysis['reason']
                        )

                elif analysis['signal'] == 'SELL' and self.engine.position > 0:
                    # 매도
                    success = self.engine.sell(
                        price=current_price,
                        timestamp=timestamp,
                        reason=analysis['reason']
                    )

                    if success:
                        last_trade = self.engine.trades[-1]
                        self.logger.log_trade(
                            trade_type='SELL',
                            price=current_price,
                            quantity=last_trade['quantity'],
                            reason=f"{analysis['reason']} | 수익률: {last_trade['profit_rate']:+.2f}%"
                        )

                # 5. 잔고 기록
                self.engine.record_balance(current_price, timestamp)

                # 6. 상태 출력
                profit_info = self.engine.get_current_profit(current_price)
                trade_summary = self.engine.get_trade_summary()

                self._print_status(analysis, profit_info, trade_summary)

                # 7. 주기적으로 대기
                time.sleep(INTERVAL)

            except KeyboardInterrupt:
                break

            except Exception as e:
                self.logger.error(f"오류 발생: {e}")
                time.sleep(INTERVAL)

        # 종료 처리
        self._shutdown()

    def _print_status(self, analysis: dict, profit_info: dict, trade_summary: dict):
        """현재 상태 출력"""
        if not analysis.get('can_trade', False):
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 분석 불가: {analysis.get('reason', '알 수 없음')}")
            return

        signal_emoji = '🟢' if analysis['signal'] == 'BUY' else '🔴' if analysis['signal'] == 'SELL' else '⚪'
        trend_emoji = '📈' if analysis['trend'] == '상승' else '📉'

        status = f"""
[{datetime.now().strftime('%H:%M:%S')}] {signal_emoji} {analysis['signal']} | {trend_emoji} {analysis['trend']}
  가격: {analysis['price']:,.0f}원 | MACD: {analysis['macd']:.2f} | Signal: {analysis['macd_signal']:.2f} | Histogram: {analysis['histogram']:.2f}"""

        if USE_TREND_FILTER:
            status += f"\n  Trend MA: {analysis['trend_ma']:,.0f}원 | 추세: {analysis['price_vs_trend']}"

        status += f"""
  💰 자산: {profit_info['total_value']:,.0f}원 | 수익: {profit_info['total_profit']:+,.0f}원 ({profit_info['total_profit_rate']:+.2f}%)
  📊 거래: {trade_summary['total_trades']}회 | 승률: {trade_summary['win_rate']:.1f}%
  📝 사유: {analysis['reason']}
"""
        print(status)

    def _shutdown(self):
        """봇 종료 처리"""
        self.logger.info("봇을 종료합니다.")

        # 최종 상태 저장
        if SAVE_TRADES and len(self.engine.trades) > 0:
            try:
                # 거래 내역 저장
                trades_df = self.engine.get_trades_df()
                trades_file = f'{LOG_DIR}/{MARKET}_macd_trades_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
                trades_df.to_csv(trades_file, index=False, encoding='utf-8-sig')
                self.logger.info(f"거래 내역 저장: {trades_file}")

                # 잔고 내역 저장
                balance_df = self.engine.get_balance_df()
                balance_file = f'{LOG_DIR}/{MARKET}_macd_balance_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
                balance_df.to_csv(balance_file, index=False, encoding='utf-8-sig')
                self.logger.info(f"잔고 내역 저장: {balance_file}")

            except Exception as e:
                self.logger.error(f"파일 저장 중 오류: {e}")

        # 최종 요약
        current_price = self.data_fetcher.get_current_price()
        if current_price:
            profit_info = self.engine.get_current_profit(current_price)
            trade_summary = self.engine.get_trade_summary()
            self.logger.log_summary(trade_summary, profit_info)

        print("\n봇이 종료되었습니다.")


if __name__ == '__main__':
    bot = MACDRealtimeTradingBot()
    bot.run()
