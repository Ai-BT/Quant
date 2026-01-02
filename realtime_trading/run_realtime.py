"""
실시간 가상 거래 봇 실행

골든크로스 + RSI 전략을 사용한 24시간 실시간 거래 시뮬레이션
"""

import time
import signal
import sys
from datetime import datetime

from config import (
    MARKET, INTERVAL, CANDLE_MINUTES, CANDLE_COUNT,
    INITIAL_CASH, COMMISSION,
    FAST_PERIOD, SLOW_PERIOD, RSI_PERIOD,
    RSI_BUY_THRESHOLD, RSI_SELL_THRESHOLD,
    LOG_DIR, SAVE_TRADES
)
from realtime_data import RealtimeDataFetcher
from paper_trading_engine import PaperTradingEngine
from goldcross_strategy import GoldenCrossStrategy
from logger import TradingLogger, print_header, print_status


class RealtimeTradingBot:
    """실시간 거래 봇 클래스"""

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
        self.strategy = GoldenCrossStrategy(
            fast_period=FAST_PERIOD,
            slow_period=SLOW_PERIOD,
            rsi_period=RSI_PERIOD,
            rsi_buy_threshold=RSI_BUY_THRESHOLD,
            rsi_sell_threshold=RSI_SELL_THRESHOLD
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
        self.logger.info(f"실시간 거래 봇 시작 - {MARKET}")
        self.logger.info(f"전략: {self.strategy.name}")
        self.logger.info(f"초기 자본: {INITIAL_CASH:,}원")
        self.logger.info(f"체크 주기: {INTERVAL}초")

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

                print_status(analysis, profit_info, trade_summary)

                # 7. 주기적으로 대기
                time.sleep(INTERVAL)

            except KeyboardInterrupt:
                break

            except Exception as e:
                self.logger.error(f"오류 발생: {e}")
                time.sleep(INTERVAL)

        # 종료 처리
        self._shutdown()

    def _shutdown(self):
        """봇 종료 처리"""
        self.logger.info("봇을 종료합니다.")

        # 최종 상태 저장
        if SAVE_TRADES and len(self.engine.trades) > 0:
            try:
                # 거래 내역 저장
                trades_df = self.engine.get_trades_df()
                trades_file = f'{LOG_DIR}/{MARKET}_trades_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
                trades_df.to_csv(trades_file, index=False, encoding='utf-8-sig')
                self.logger.info(f"거래 내역 저장: {trades_file}")

                # 잔고 내역 저장
                balance_df = self.engine.get_balance_df()
                balance_file = f'{LOG_DIR}/{MARKET}_balance_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
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
    bot = RealtimeTradingBot()
    bot.run()
