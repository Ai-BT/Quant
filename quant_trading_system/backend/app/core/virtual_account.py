"""
가상 계좌 관리 시스템

가상 자금으로 전략을 테스트하기 위한 계좌 관리
"""

from typing import Dict, List, Optional
from datetime import datetime
from decimal import Decimal, ROUND_DOWN
from app.core.logging import get_logger

logger = get_logger(__name__, "virtual_account")


class VirtualAccount:
    """가상 계좌"""
    
    def __init__(self, initial_balance: float = 10_000_000):
        """
        Parameters
        ----------
        initial_balance : float
            초기 잔고 (기본 1000만원)
        """
        self.initial_balance = Decimal(str(initial_balance))
        self.balance = Decimal(str(initial_balance))  # KRW 잔고
        self.holdings: Dict[str, Decimal] = {}  # {currency: quantity}
        self.avg_buy_prices: Dict[str, Decimal] = {}  # {currency: avg_buy_price} - 평균 매수가 추적
        self.trade_history: List[Dict] = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def get_balance(self) -> float:
        """현재 KRW 잔고 조회"""
        return float(self.balance)
    
    def get_holdings(self) -> Dict[str, float]:
        """보유 코인 조회"""
        return {currency: float(quantity) for currency, quantity in self.holdings.items()}
    
    def get_avg_buy_prices(self) -> Dict[str, float]:
        """평균 매수가 조회"""
        return {currency: float(avg_price) for currency, avg_price in self.avg_buy_prices.items()}
    
    def get_total_value(self, prices: Dict[str, float]) -> float:
        """총 자산 가치 계산 (KRW + 코인 평가액)"""
        total = float(self.balance)
        for currency, quantity in self.holdings.items():
            if currency in prices:
                total += float(quantity) * prices[currency]
        return total
    
    def buy(self, currency: str, price: float, quantity: Optional[float] = None, amount: Optional[float] = None, commission: float = 0.0005) -> bool:
        """
        매수
        
        Parameters
        ----------
        currency : str
            코인 심볼 (예: 'BTC')
        price : float
            매수가격
        quantity : float, optional
            매수 수량 (amount와 둘 중 하나만 지정)
        amount : float, optional
            매수 금액 (quantity와 둘 중 하나만 지정)
        commission : float
            수수료율 (기본 0.05%)
        
        Returns
        -------
        bool
            성공 여부
        """
        price_decimal = Decimal(str(price))
        commission_decimal = Decimal(str(commission))
        
        if amount:
            # 금액으로 매수
            amount_decimal = Decimal(str(amount))
            if amount_decimal > self.balance:
                logger.warning(f"잔고 부족: {amount_decimal} > {self.balance}")
                return False
            
            # 수수료 제외한 실제 매수 금액
            available_amount = amount_decimal * (Decimal('1') - commission_decimal)
            quantity_decimal = available_amount / price_decimal
            actual_amount = amount_decimal
        elif quantity:
            # 수량으로 매수
            quantity_decimal = Decimal(str(quantity))
            required_amount = quantity_decimal * price_decimal / (Decimal('1') - commission_decimal)
            if required_amount > self.balance:
                logger.warning(f"잔고 부족: {required_amount} > {self.balance}")
                return False
            actual_amount = required_amount
        else:
            logger.error("quantity 또는 amount 중 하나를 지정해야 합니다")
            return False
        
        # 잔고 차감
        self.balance -= actual_amount
        
        # 보유 코인 추가 및 평균 매수가 계산 (가중평균)
        if currency in self.holdings:
            # 기존 보유량과 평균 매수가
            old_quantity = self.holdings[currency]
            old_avg_price = self.avg_buy_prices.get(currency, price_decimal)
            old_total_value = old_quantity * old_avg_price
            
            # 새로운 매수 금액
            new_total_value = quantity_decimal * price_decimal
            
            # 새로운 평균 매수가 (가중평균)
            total_quantity = old_quantity + quantity_decimal
            new_avg_price = (old_total_value + new_total_value) / total_quantity
            
            self.holdings[currency] = total_quantity
            self.avg_buy_prices[currency] = new_avg_price
        else:
            self.holdings[currency] = quantity_decimal
            self.avg_buy_prices[currency] = price_decimal
        
        # 거래 기록
        trade = {
            'type': 'BUY',
            'currency': currency,
            'price': float(price_decimal),
            'quantity': float(quantity_decimal),
            'amount': float(actual_amount),
            'commission': float(actual_amount * commission_decimal),
            'timestamp': datetime.now().isoformat(),
            'balance_after': float(self.balance),
        }
        self.trade_history.append(trade)
        self.updated_at = datetime.now()
        
        logger.info(f"매수 완료: {currency} {float(quantity_decimal)}개 @ {price}원 (금액: {float(actual_amount):,.0f}원)")
        return True
    
    def sell(self, currency: str, price: float, quantity: Optional[float] = None, ratio: Optional[float] = None, commission: float = 0.0005) -> bool:
        """
        매도
        
        Parameters
        ----------
        currency : str
            코인 심볼 (예: 'BTC')
        price : float
            매도가격
        quantity : float, optional
            매도 수량 (ratio와 둘 중 하나만 지정)
        ratio : float, optional
            매도 비율 (0.0 ~ 1.0, quantity와 둘 중 하나만 지정)
        commission : float
            수수료율 (기본 0.05%)
        
        Returns
        -------
        bool
            성공 여부
        """
        if currency not in self.holdings or self.holdings[currency] <= 0:
            logger.warning(f"보유 코인 없음: {currency}")
            return False
        
        price_decimal = Decimal(str(price))
        commission_decimal = Decimal(str(commission))
        available_quantity = self.holdings[currency]
        
        if ratio:
            # 비율로 매도
            ratio_decimal = Decimal(str(ratio))
            quantity_decimal = available_quantity * ratio_decimal
        elif quantity:
            # 수량으로 매도
            quantity_decimal = Decimal(str(quantity))
            if quantity_decimal > available_quantity:
                quantity_decimal = available_quantity  # 전체 매도
        else:
            # 전체 매도
            quantity_decimal = available_quantity
        
        # 매도 금액 계산 (수수료 제외)
        gross_amount = quantity_decimal * price_decimal
        net_amount = gross_amount * (Decimal('1') - commission_decimal)
        
        # 잔고 추가
        self.balance += net_amount
        
        # 보유 코인 차감
        self.holdings[currency] -= quantity_decimal
        if self.holdings[currency] <= Decimal('0'):
            del self.holdings[currency]
            # 보유 코인이 0이 되면 평균 매수가도 삭제
            if currency in self.avg_buy_prices:
                del self.avg_buy_prices[currency]
        
        # 거래 기록
        trade = {
            'type': 'SELL',
            'currency': currency,
            'price': float(price_decimal),
            'quantity': float(quantity_decimal),
            'amount': float(net_amount),
            'commission': float(gross_amount * commission_decimal),
            'timestamp': datetime.now().isoformat(),
            'balance_after': float(self.balance),
        }
        self.trade_history.append(trade)
        self.updated_at = datetime.now()
        
        logger.info(f"매도 완료: {currency} {float(quantity_decimal)}개 @ {price}원 (금액: {float(net_amount):,.0f}원)")
        return True
    
    def get_trade_history(self, limit: Optional[int] = None) -> List[Dict]:
        """거래 내역 조회"""
        history = self.trade_history.copy()
        if limit:
            history = history[-limit:]
        return list(reversed(history))
    
    def get_summary(self, prices: Optional[Dict[str, float]] = None) -> Dict:
        """계좌 요약 정보"""
        total_value = self.get_total_value(prices or {})
        profit_loss = total_value - float(self.initial_balance)
        profit_loss_rate = (profit_loss / float(self.initial_balance)) * 100
        
        return {
            'initial_balance': float(self.initial_balance),
            'current_balance': float(self.balance),
            'holdings': self.get_holdings(),
            'total_value': total_value,
            'profit_loss': profit_loss,
            'profit_loss_rate': profit_loss_rate,
            'num_trades': len(self.trade_history),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


# 전역 가상 계좌 인스턴스
virtual_account = VirtualAccount(initial_balance=10_000_000)

