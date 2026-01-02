"""
Mock API: Paper trading용 가상 거래소 API
"""
from typing import Optional, Dict, List
from datetime import datetime
import uuid


class MockExchangeAPI:
    """Mock 거래소 API (Paper Trading)"""
    
    def __init__(self, initial_balance: float = 1_000_000):
        """
        초기화
        
        Parameters
        ----------
        initial_balance : float
            초기 잔고 (원화)
        """
        self.balance = initial_balance
        self.holdings: Dict[str, float] = {}  # symbol -> quantity
        self.orders: Dict[str, Dict] = {}
        self.current_prices: Dict[str, float] = {}  # symbol -> price
    
    def set_price(self, symbol: str, price: float):
        """현재 가격 설정 (테스트용)"""
        self.current_prices[symbol] = price
    
    def get_ticker(self, symbol: str) -> Dict:
        """
        현재가 조회
        
        Returns
        -------
        dict
            ticker 정보
        """
        price = self.current_prices.get(symbol, 100_000)  # 기본값
        
        return {
            "market": symbol,
            "trade_price": price,
            "trade_time": datetime.utcnow().isoformat()
        }
    
    def get_balance(self) -> Dict:
        """
        잔고 조회
        
        Returns
        -------
        dict
            잔고 정보
        """
        total_value = self.balance
        
        for symbol, quantity in self.holdings.items():
            price = self.current_prices.get(symbol, 0)
            total_value += quantity * price
        
        return {
            "balance": self.balance,
            "holdings": self.holdings.copy(),
            "total_value": total_value
        }
    
    def place_order(self, symbol: str, side: str, order_type: str,
                   price: Optional[float] = None, 
                   quantity: Optional[float] = None,
                   volume: Optional[float] = None) -> Dict:
        """
        주문 실행
        
        Parameters
        ----------
        symbol : str
            심볼
        side : str
            'bid' (매수) 또는 'ask' (매도)
        order_type : str
            'limit' 또는 'market'
        price : float, optional
            지정가 가격 (limit 주문 시 필수)
        quantity : float, optional
            주문 수량
        volume : float, optional
            주문 금액 (매수 시 사용)
        
        Returns
        -------
        dict
            주문 정보
        """
        order_id = str(uuid.uuid4())
        current_price = self.current_prices.get(symbol, 100_000)
        
        # 지정가 주문이면 지정 가격 사용, 시장가면 현재가 사용
        execution_price = price if order_type == "limit" and price else current_price
        
        if side == "bid":  # 매수
            if volume:
                quantity = volume / execution_price
            elif not quantity:
                raise ValueError("quantity or volume required for buy order")
            
            cost = quantity * execution_price
            if cost > self.balance:
                raise ValueError(f"Insufficient balance: {cost} > {self.balance}")
            
            self.balance -= cost
            self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity
        
        else:  # 매도
            if not quantity:
                raise ValueError("quantity required for sell order")
            
            current_holding = self.holdings.get(symbol, 0)
            if quantity > current_holding:
                raise ValueError(f"Insufficient holdings: {quantity} > {current_holding}")
            
            revenue = quantity * execution_price
            self.balance += revenue
            self.holdings[symbol] = current_holding - quantity
            
            if self.holdings[symbol] <= 0:
                del self.holdings[symbol]
        
        order = {
            "uuid": order_id,
            "market": symbol,
            "side": side,
            "order_type": order_type,
            "price": execution_price,
            "quantity": quantity,
            "executed_volume": quantity * execution_price,
            "state": "done",
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.orders[order_id] = order
        
        return order
    
    def get_order(self, order_id: str) -> Optional[Dict]:
        """주문 조회"""
        return self.orders.get(order_id)
    
    def get_candles(self, symbol: str, timeframe: str, count: int = 200) -> List[Dict]:
        """
        캔들 데이터 조회 (Mock)
        
        실제로는 거래소 API를 호출해야 하지만, 
        여기서는 빈 리스트 반환 (실제 구현 필요)
        """
        # 실제 구현에서는 거래소 API 호출
        return []

