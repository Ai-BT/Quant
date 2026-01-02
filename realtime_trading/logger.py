"""
로깅 유틸리티

거래 내역 및 시스템 로그를 파일과 콘솔에 기록
"""

import os
import logging
from datetime import datetime
from typing import Dict


class TradingLogger:
    """거래 로거 클래스"""

    def __init__(self, log_dir: str = 'logs', market: str = 'KRW-BTC'):
        """
        Parameters
        ----------
        log_dir : str
            로그 파일 디렉토리
        market : str
            마켓 코드
        """
        self.log_dir = log_dir
        self.market = market

        # 로그 디렉토리 생성
        os.makedirs(log_dir, exist_ok=True)

        # 로그 파일명 (날짜별)
        today = datetime.now().strftime('%Y%m%d')
        self.log_file = os.path.join(log_dir, f'{market}_{today}.log')
        self.trade_log_file = os.path.join(log_dir, f'{market}_{today}_trades.log')

        # 로거 설정
        self._setup_logger()

    def _setup_logger(self):
        """로거 설정"""
        # 메인 로거
        self.logger = logging.getLogger(f'TradingBot_{self.market}')
        self.logger.setLevel(logging.INFO)

        # 기존 핸들러 제거
        self.logger.handlers.clear()

        # 파일 핸들러
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)

        # 콘솔 핸들러
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 포맷터
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # 거래 로거
        self.trade_logger = logging.getLogger(f'TradingBot_{self.market}_Trades')
        self.trade_logger.setLevel(logging.INFO)
        self.trade_logger.handlers.clear()

        trade_file_handler = logging.FileHandler(self.trade_log_file, encoding='utf-8')
        trade_file_handler.setLevel(logging.INFO)
        trade_file_handler.setFormatter(formatter)
        self.trade_logger.addHandler(trade_file_handler)

    def info(self, message: str):
        """정보 로그"""
        self.logger.info(message)

    def warning(self, message: str):
        """경고 로그"""
        self.logger.warning(message)

    def error(self, message: str):
        """에러 로그"""
        self.logger.error(message)

    def log_trade(self, trade_type: str, price: float, quantity: float, reason: str):
        """
        거래 로그 기록

        Parameters
        ----------
        trade_type : str
            거래 유형 (BUY/SELL)
        price : float
            거래 가격
        quantity : float
            거래 수량
        reason : str
            거래 사유
        """
        message = f'{trade_type} | Price: {price:,.0f} | Quantity: {quantity:.8f} | Reason: {reason}'
        self.trade_logger.info(message)
        self.info(message)

    def log_analysis(self, analysis: Dict):
        """
        분석 결과 로그

        Parameters
        ----------
        analysis : dict
            분석 결과
        """
        if not analysis.get('can_trade', False):
            self.info(f"분석 불가: {analysis.get('reason', '알 수 없음')}")
            return

        message = (
            f"신호: {analysis['signal']} | "
            f"가격: {analysis['price']:,.0f} | "
            f"SMA({self.market}): {analysis['sma_fast']:,.0f}/{analysis['sma_slow']:,.0f} | "
            f"RSI: {analysis['rsi']:.1f} | "
            f"추세: {analysis['trend']} | "
            f"사유: {analysis['reason']}"
        )
        self.info(message)

    def log_balance(self, profit_info: Dict):
        """
        잔고 정보 로그

        Parameters
        ----------
        profit_info : dict
            수익 정보
        """
        message = (
            f"💰 총자산: {profit_info['total_value']:,.0f}원 | "
            f"수익: {profit_info['total_profit']:+,.0f}원 ({profit_info['total_profit_rate']:+.2f}%) | "
            f"현금: {profit_info['cash']:,.0f}원 | "
            f"포지션: {profit_info['position']:.8f}"
        )
        self.info(message)

    def log_summary(self, trade_summary: Dict, profit_info: Dict):
        """
        거래 요약 로그

        Parameters
        ----------
        trade_summary : dict
            거래 요약 정보
        profit_info : dict
            수익 정보
        """
        summary = f"""
{'='*60}
거래 요약
{'='*60}
총 거래 횟수: {trade_summary['total_trades']}
매수: {trade_summary['buy_count']} | 매도: {trade_summary['sell_count']}
승: {trade_summary['win_count']} | 패: {trade_summary['lose_count']}
승률: {trade_summary['win_rate']:.2f}%
평균 수익률: {trade_summary['avg_profit_rate']:.2f}%
{'='*60}
최종 자산: {profit_info['total_value']:,.0f}원
총 수익: {profit_info['total_profit']:+,.0f}원 ({profit_info['total_profit_rate']:+.2f}%)
{'='*60}
"""
        self.info(summary)


def print_header(market: str, strategy_name: str):
    """
    프로그램 시작 헤더 출력

    Parameters
    ----------
    market : str
        마켓 코드
    strategy_name : str
        전략 이름
    """
    header = f"""
{'='*60}
🤖 실시간 가상 거래 봇 시작
{'='*60}
마켓: {market}
전략: {strategy_name}
시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}
"""
    print(header)


def print_status(analysis: Dict, profit_info: Dict, trade_summary: Dict):
    """
    현재 상태 출력 (간단한 형식)

    Parameters
    ----------
    analysis : dict
        분석 결과
    profit_info : dict
        수익 정보
    trade_summary : dict
        거래 요약
    """
    if not analysis.get('can_trade', False):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 분석 불가: {analysis.get('reason', '알 수 없음')}")
        return

    signal_emoji = '🟢' if analysis['signal'] == 'BUY' else '🔴' if analysis['signal'] == 'SELL' else '⚪'
    trend_emoji = '📈' if analysis['trend'] == '상승' else '📉'

    status = f"""
[{datetime.now().strftime('%H:%M:%S')}] {signal_emoji} {analysis['signal']} | {trend_emoji} {analysis['trend']}
  가격: {analysis['price']:,.0f}원 | RSI: {analysis['rsi']:.1f} | SMA: {analysis['sma_fast']:,.0f}/{analysis['sma_slow']:,.0f}
  💰 자산: {profit_info['total_value']:,.0f}원 | 수익: {profit_info['total_profit']:+,.0f}원 ({profit_info['total_profit_rate']:+.2f}%)
  📊 거래: {trade_summary['total_trades']}회 | 승률: {trade_summary['win_rate']:.1f}%
  📝 사유: {analysis['reason']}
"""
    print(status)
