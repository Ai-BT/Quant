"""
실행 모듈: 주문 실행, 중복 방지, paper trading
"""
from typing import Optional, Dict
import uuid
from datetime import datetime
from app.core.state_machine import PositionState
from app.core.database import Database
from app.core.logger import setup_logger
from app.api.mock_api import MockExchangeAPI

logger = setup_logger(__name__)


class OrderExecutor:
    """주문 실행기"""
    
    def __init__(self, exchange_api: MockExchangeAPI, db: Database, symbol: str):
        """
        초기화
        
        Parameters
        ----------
        exchange_api : MockExchangeAPI
            거래소 API (Mock 또는 실제)
        db : Database
            데이터베이스
        symbol : str
            거래 심볼
        """
        self.exchange_api = exchange_api
        self.db = db
        self.symbol = symbol
    
    def execute_order(self, action: str, price: float, 
                     quantity: Optional[float] = None,
                     order_type: str = "market",
                     decision_id: Optional[int] = None) -> Dict:
        """
        주문 실행 (중복 방지 포함)
        
        Parameters
        ----------
        action : str
            'BUY' 또는 'SELL'
        price : float
            가격
        quantity : float, optional
            수량 (None이면 잔고 기반으로 계산)
        order_type : str
            'market' 또는 'limit'
        decision_id : int, optional
            결정 ID (트레이싱용)
        
        Returns
        -------
        dict
            주문 결과
        """
        # 주문 ID 생성 (idempotency key)
        order_id = str(uuid.uuid4())
        
        # 중복 확인
        if self.db.check_order_exists(order_id):
            logger.warning(f"Order ID {order_id} already exists (duplicate)")
            existing_order = self.db.get_connection().execute(
                "SELECT * FROM orders WHERE order_id = ?", (order_id,)
            ).fetchone()
            return {
                'success': False,
                'error': 'Order ID already exists',
                'order_id': order_id,
                'order': dict(existing_order) if existing_order else None
            }
        
        side = "bid" if action == "BUY" else "ask"
        
        try:
            # 주문 실행
            order_result = self.exchange_api.place_order(
                symbol=self.symbol,
                side=side,
                order_type=order_type,
                price=price if order_type == "limit" else None,
                quantity=quantity,
                volume=None if quantity else None  # 필요시 구현
            )
            
            # DB에 주문 기록 (idempotency)
            self.db.insert_order(
                order_id=order_id,
                symbol=self.symbol,
                order_type=order_type,
                side=side,
                price=price,
                quantity=order_result.get('quantity'),
                status=order_result.get('state', 'done'),
                executed_at=datetime.utcnow(),
                metadata={'decision_id': decision_id}
            )
            
            # 액션 기록
            state_before = "UNKNOWN"  # 실제로는 state machine에서 가져와야 함
            state_after = "LONG" if action == "BUY" else "FLAT"
            
            self.db.insert_action(
                symbol=self.symbol,
                action_type=action,
                order_type=order_type,
                price=price,
                quantity=order_result.get('quantity'),
                state_before=state_before,
                state_after=state_after,
                order_id=order_id,
                status="DONE",
                metadata={'decision_id': decision_id}
            )
            
            logger.info(f"Order executed: {action} {order_result.get('quantity')} @ {price} "
                       f"(order_id={order_id})")
            
            return {
                'success': True,
                'order_id': order_id,
                'order': order_result
            }
        
        except Exception as e:
            logger.error(f"Order execution failed: {e}")
            
            # 실패한 주문도 기록
            try:
                self.db.insert_order(
                    order_id=order_id,
                    symbol=self.symbol,
                    order_type=order_type,
                    side=side,
                    price=price,
                    quantity=quantity,
                    status="FAILED",
                    metadata={'error': str(e), 'decision_id': decision_id}
                )
            except:
                pass
            
            return {
                'success': False,
                'error': str(e),
                'order_id': order_id
            }
    
    def execute_decision(self, decision: Dict, current_price: float) -> Dict:
        """
        결정을 실행으로 변환
        
        Parameters
        ----------
        decision : dict
            DecisionEngine.decide()의 결과
        current_price : float
            현재 가격
        
        Returns
        -------
        dict
            실행 결과
        """
        action = decision.get('action')
        
        if action == 'HOLD':
            return {
                'executed': False,
                'reason': 'HOLD action, no order executed'
            }
        
        # BUY 또는 SELL 주문 실행
        quantity = None  # Mock API에서 자동 계산되거나 전략에서 결정
        
        result = self.execute_order(
            action=action,
            price=current_price,
            quantity=quantity,
            order_type="market",
            decision_id=decision.get('metadata', {}).get('decision_id')
        )
        
        return {
            'executed': result.get('success', False),
            'order_result': result
        }

