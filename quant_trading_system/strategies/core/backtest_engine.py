"""
백테스팅 엔진

가상의 돈으로 전략을 백테스팅하는 시스템
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Trade:
    """거래 기록"""
    date: datetime
    type: str  # 'BUY' or 'SELL'
    price: float
    quantity: float
    cash_before: float
    cash_after: float
    holdings_before: float
    holdings_after: float
    portfolio_value: float


class Portfolio:
    """가상 포트폴리오"""
    
    def __init__(self, initial_cash: float = 1_000_000, commission: float = 0.0005):
        """
        Parameters
        ----------
        initial_cash : float
            초기 자본금 (기본 100만원)
        commission : float
            수수료율 (기본 0.05%)
        """
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.holdings = 0.0  # 보유 코인 수
        self.commission = commission
        self.trades: List[Trade] = []
        self.portfolio_values: List[float] = []
        self.dates: List[datetime] = []
    
    def buy(self, date: datetime, price: float) -> bool:
        """매수"""
        if self.cash <= 0:
            return False
        
        available_cash = self.cash * (1 - self.commission)
        quantity = available_cash / price
        
        if quantity <= 0:
            return False
        
        cash_before = self.cash
        holdings_before = self.holdings
        
        self.cash = 0
        self.holdings += quantity
        
        portfolio_value = self.cash + (self.holdings * price)
        
        trade = Trade(
            date=date,
            type='BUY',
            price=price,
            quantity=quantity,
            cash_before=cash_before,
            cash_after=self.cash,
            holdings_before=holdings_before,
            holdings_after=self.holdings,
            portfolio_value=portfolio_value
        )
        
        self.trades.append(trade)
        return True
    
    def sell(self, date: datetime, price: float) -> bool:
        """매도"""
        if self.holdings <= 0:
            return False
        
        sell_amount = self.holdings * price * (1 - self.commission)
        
        cash_before = self.cash
        holdings_before = self.holdings
        
        self.cash = sell_amount
        self.holdings = 0
        
        portfolio_value = self.cash + (self.holdings * price)
        
        trade = Trade(
            date=date,
            type='SELL',
            price=price,
            quantity=holdings_before,
            cash_before=cash_before,
            cash_after=self.cash,
            holdings_before=holdings_before,
            holdings_after=self.holdings,
            portfolio_value=portfolio_value
        )
        
        self.trades.append(trade)
        return True
    
    def update_value(self, date: datetime, price: float):
        """포트폴리오 가치 업데이트"""
        portfolio_value = self.cash + (self.holdings * price)
        self.portfolio_values.append(portfolio_value)
        self.dates.append(date)
    
    def finalize(self, final_price: float):
        """최종 정산"""
        if self.holdings > 0:
            self.cash = self.holdings * final_price * (1 - self.commission)
            self.holdings = 0
    
    def get_final_value(self) -> float:
        """최종 포트폴리오 가치"""
        return self.cash
    
    def get_total_return(self) -> float:
        """총 수익률 (%)"""
        final_value = self.get_final_value()
        return ((final_value / self.initial_cash) - 1) * 100


class BacktestEngine:
    """백테스팅 엔진"""
    
    def __init__(self, initial_cash: float = 1_000_000, commission: float = 0.0005):
        """
        Parameters
        ----------
        initial_cash : float
            초기 자본금
        commission : float
            수수료율
        """
        self.initial_cash = initial_cash
        self.commission = commission
    
    def run(self, df: pd.DataFrame, signals: pd.DataFrame) -> Dict:
        """
        백테스팅 실행
        
        Parameters
        ----------
        df : pd.DataFrame
            가격 데이터
        signals : pd.DataFrame
            매매 신호 (signal, position 컬럼 필요)
        
        Returns
        -------
        dict
            백테스팅 결과
        """
        df = df.copy()
        df['signal'] = signals['signal']
        df['position'] = signals['position']
        
        portfolio = Portfolio(
            initial_cash=self.initial_cash,
            commission=self.commission
        )
        
        for i in range(len(df)):
            date = df.index[i]  # 날짜가 이제 인덱스
            price = df.iloc[i]['종가']
            position = df.iloc[i]['position']
            
            if position == 1:
                portfolio.buy(date, price)
            elif position == -1:
                portfolio.sell(date, price)
            
            portfolio.update_value(date, price)
        
        final_price = df.iloc[-1]['종가']
        portfolio.finalize(final_price)
        
        results = self._calculate_metrics(df, portfolio)
        return results
    
    def _calculate_metrics(self, df: pd.DataFrame, portfolio: Portfolio) -> Dict:
        """성과 지표 계산"""
        total_return = portfolio.get_total_return()
        final_value = portfolio.get_final_value()
        
        portfolio_df = pd.DataFrame({
            'date': portfolio.dates,
            'portfolio_value': portfolio.portfolio_values
        })
        
        if len(portfolio_df) == 0:
            return {
                'total_return': 0,
                'final_value': self.initial_cash,
                'num_trades': 0,
                'mdd': 0,
                'sharpe_ratio': 0,
                'win_rate': 0,
                'trades': [],
                'portfolio_df': pd.DataFrame()
            }
        
        portfolio_df['returns'] = portfolio_df['portfolio_value'].pct_change()
        
        # MDD
        cummax = portfolio_df['portfolio_value'].expanding().max()
        drawdown = (portfolio_df['portfolio_value'] - cummax) / cummax
        mdd = drawdown.min() * 100
        
        # 샤프 비율
        risk_free_rate = 0.02 / 365
        excess_returns = portfolio_df['returns'] - risk_free_rate
        sharpe_ratio = (
            (excess_returns.mean() / excess_returns.std()) * np.sqrt(365)
            if excess_returns.std() != 0 else 0
        )
        
        # 승률
        profits = []
        for i in range(0, len(portfolio.trades) - 1, 2):
            if (i + 1 < len(portfolio.trades) and 
                portfolio.trades[i].type == 'BUY' and 
                portfolio.trades[i + 1].type == 'SELL'):
                profit = (portfolio.trades[i + 1].portfolio_value - 
                          portfolio.trades[i].portfolio_value)
                profits.append(profit)
        
        win_count = len([p for p in profits if p > 0])
        win_rate = (win_count / len(profits) * 100) if len(profits) > 0 else 0
        
        # Buy & Hold
        buy_hold_return = ((df.iloc[-1]['종가'] / df.iloc[0]['종가']) - 1) * 100
        
        # 순이익
        net_profit = final_value - self.initial_cash
        
        return {
            'initial_cash': self.initial_cash,
            'final_value': final_value,
            'net_profit': net_profit,
            'total_return': total_return,
            'buy_hold_return': buy_hold_return,
            'mdd': mdd,
            'sharpe_ratio': sharpe_ratio,
            'num_trades': len(portfolio.trades),
            'win_rate': win_rate,
            'trades': portfolio.trades,
            'portfolio_df': portfolio_df,
            'dates': portfolio.dates,
            'portfolio_values': portfolio.portfolio_values
        }
    
    @staticmethod
    def print_results(result: Dict):
        """결과 출력"""
        print("=" * 70)
        print("📊 백테스팅 결과")
        print("=" * 70)
        print(f"💰 초기 자본:     {result['initial_cash']:>12,.0f}원")
        print(f"💰 최종 자산:     {result['final_value']:>12,.0f}원")
        print(f"📈 총 수익률:     {result['total_return']:>12.2f}%")
        print(f"📊 Buy & Hold:    {result['buy_hold_return']:>12.2f}%")
        print(f"📉 MDD (최대낙폭): {result['mdd']:>12.2f}%")
        print(f"📊 샤프 비율:     {result['sharpe_ratio']:>12.2f}")
        print(f"🔄 거래 횟수:     {result['num_trades']:>12}회")
        print(f"🎯 승률:          {result['win_rate']:>12.1f}%")
        print("=" * 70)


