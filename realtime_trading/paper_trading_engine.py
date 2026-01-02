"""
가상 거래 엔진 (Paper Trading Engine)

실제 돈을 사용하지 않고 가상으로 거래를 시뮬레이션하는 엔진
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional


class PaperTradingEngine:
    """가상 거래 엔진 클래스"""

    def __init__(self, initial_cash: float, commission: float = 0.0005):
        """
        Parameters
        ----------
        initial_cash : float
            초기 자본금
        commission : float
            수수료율 (기본 0.05%)
        """
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.commission = commission

        # 포지션 정보
        self.position = 0.0  # 보유 코인 수량
        self.avg_buy_price = 0.0  # 평균 매수가

        # 거래 내역
        self.trades: List[Dict] = []
        self.balance_history: List[Dict] = []

    def buy(self, price: float, timestamp: datetime, reason: str = "") -> bool:
        """
        매수 주문

        Parameters
        ----------
        price : float
            매수 가격
        timestamp : datetime
            거래 시각
        reason : str
            매수 사유

        Returns
        -------
        bool
            매수 성공 여부
        """
        # 이미 포지션이 있으면 매수하지 않음
        if self.position > 0:
            return False

        # 수수료를 고려한 매수 금액
        amount_with_commission = self.cash * (1 - self.commission)
        quantity = amount_with_commission / price

        if quantity > 0:
            self.position = quantity
            self.avg_buy_price = price
            self.cash = 0

            # 거래 내역 기록
            trade = {
                'timestamp': timestamp,
                'type': 'BUY',
                'price': price,
                'quantity': quantity,
                'amount': amount_with_commission,
                'commission': self.cash * self.commission if self.cash > 0 else 0,
                'reason': reason,
                'balance': self.get_total_value(price)
            }
            self.trades.append(trade)

            return True

        return False

    def sell(self, price: float, timestamp: datetime, reason: str = "") -> bool:
        """
        매도 주문

        Parameters
        ----------
        price : float
            매도 가격
        timestamp : datetime
            거래 시각
        reason : str
            매도 사유

        Returns
        -------
        bool
            매도 성공 여부
        """
        # 포지션이 없으면 매도하지 않음
        if self.position <= 0:
            return False

        # 수수료를 고려한 매도 금액
        sell_amount = self.position * price
        amount_after_commission = sell_amount * (1 - self.commission)

        # 수익률 계산
        profit = (price - self.avg_buy_price) * self.position
        profit_rate = ((price - self.avg_buy_price) / self.avg_buy_price) * 100

        self.cash = amount_after_commission

        # 거래 내역 기록
        trade = {
            'timestamp': timestamp,
            'type': 'SELL',
            'price': price,
            'quantity': self.position,
            'amount': amount_after_commission,
            'commission': sell_amount * self.commission,
            'buy_price': self.avg_buy_price,
            'profit': profit,
            'profit_rate': profit_rate,
            'reason': reason,
            'balance': self.get_total_value(price)
        }
        self.trades.append(trade)

        # 포지션 초기화
        self.position = 0.0
        self.avg_buy_price = 0.0

        return True

    def get_total_value(self, current_price: float) -> float:
        """
        총 자산 가치 계산

        Parameters
        ----------
        current_price : float
            현재 가격

        Returns
        -------
        float
            총 자산 가치 (현금 + 보유 코인 가치)
        """
        position_value = self.position * current_price
        return self.cash + position_value

    def get_current_profit(self, current_price: float) -> Dict:
        """
        현재 수익 정보 계산

        Parameters
        ----------
        current_price : float
            현재 가격

        Returns
        -------
        dict
            수익 정보
        """
        total_value = self.get_total_value(current_price)
        total_profit = total_value - self.initial_cash
        total_profit_rate = (total_profit / self.initial_cash) * 100

        # 미실현 수익 (현재 포지션이 있는 경우)
        unrealized_profit = 0
        unrealized_profit_rate = 0
        if self.position > 0:
            unrealized_profit = (current_price - self.avg_buy_price) * self.position
            unrealized_profit_rate = ((current_price - self.avg_buy_price) / self.avg_buy_price) * 100

        return {
            'total_value': total_value,
            'total_profit': total_profit,
            'total_profit_rate': total_profit_rate,
            'unrealized_profit': unrealized_profit,
            'unrealized_profit_rate': unrealized_profit_rate,
            'cash': self.cash,
            'position': self.position,
            'avg_buy_price': self.avg_buy_price
        }

    def record_balance(self, current_price: float, timestamp: datetime):
        """
        잔고 내역 기록

        Parameters
        ----------
        current_price : float
            현재 가격
        timestamp : datetime
            기록 시각
        """
        profit_info = self.get_current_profit(current_price)

        balance = {
            'timestamp': timestamp,
            'price': current_price,
            'cash': self.cash,
            'position': self.position,
            'total_value': profit_info['total_value'],
            'total_profit': profit_info['total_profit'],
            'total_profit_rate': profit_info['total_profit_rate']
        }
        self.balance_history.append(balance)

    def get_trade_summary(self) -> Dict:
        """
        거래 요약 정보

        Returns
        -------
        dict
            거래 요약
        """
        if not self.trades:
            return {
                'total_trades': 0,
                'buy_count': 0,
                'sell_count': 0,
                'win_count': 0,
                'lose_count': 0,
                'win_rate': 0,
                'avg_profit_rate': 0
            }

        buy_count = sum(1 for t in self.trades if t['type'] == 'BUY')
        sell_count = sum(1 for t in self.trades if t['type'] == 'SELL')

        sell_trades = [t for t in self.trades if t['type'] == 'SELL']
        win_count = sum(1 for t in sell_trades if t['profit'] > 0)
        lose_count = sum(1 for t in sell_trades if t['profit'] <= 0)

        win_rate = (win_count / sell_count * 100) if sell_count > 0 else 0
        avg_profit_rate = sum(t['profit_rate'] for t in sell_trades) / sell_count if sell_count > 0 else 0

        return {
            'total_trades': len(self.trades),
            'buy_count': buy_count,
            'sell_count': sell_count,
            'win_count': win_count,
            'lose_count': lose_count,
            'win_rate': win_rate,
            'avg_profit_rate': avg_profit_rate
        }

    def get_trades_df(self) -> pd.DataFrame:
        """
        거래 내역을 DataFrame으로 반환

        Returns
        -------
        pd.DataFrame
            거래 내역
        """
        if not self.trades:
            return pd.DataFrame()

        return pd.DataFrame(self.trades)

    def get_balance_df(self) -> pd.DataFrame:
        """
        잔고 내역을 DataFrame으로 반환

        Returns
        -------
        pd.DataFrame
            잔고 내역
        """
        if not self.balance_history:
            return pd.DataFrame()

        return pd.DataFrame(self.balance_history)
