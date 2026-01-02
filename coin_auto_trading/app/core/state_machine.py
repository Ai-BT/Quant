"""
상태 머신: 포지션 상태 관리 (FLAT/LONG/PENDING)
"""
from enum import Enum
from typing import Optional
from datetime import datetime


class PositionState(Enum):
    """포지션 상태"""
    FLAT = "FLAT"  # 포지션 없음
    LONG = "LONG"  # 매수 포지션 보유
    PENDING = "PENDING"  # 주문 대기 중


class StateMachine:
    """포지션 상태 머신"""
    
    def __init__(self, initial_state: PositionState = PositionState.FLAT):
        self.state = initial_state
        self.transition_history = []
        self.current_position: Optional[dict] = None
    
    def transition_to(self, new_state: PositionState, reason: str = "", metadata: dict = None):
        """
        상태 전환
        
        Parameters
        ----------
        new_state : PositionState
            새로운 상태
        reason : str
            전환 사유
        metadata : dict, optional
            추가 메타데이터
        """
        old_state = self.state
        
        # 유효한 전환인지 확인
        if not self._is_valid_transition(old_state, new_state):
            raise ValueError(
                f"Invalid transition from {old_state.value} to {new_state.value}"
            )
        
        self.state = new_state
        
        transition_record = {
            "timestamp": datetime.utcnow(),
            "from_state": old_state.value,
            "to_state": new_state.value,
            "reason": reason,
            "metadata": metadata or {}
        }
        
        self.transition_history.append(transition_record)
        
        return transition_record
    
    def _is_valid_transition(self, from_state: PositionState, to_state: PositionState) -> bool:
        """
        유효한 상태 전환인지 확인
        
        FLAT -> LONG (매수 주문)
        FLAT -> PENDING (매수 주문 중)
        LONG -> FLAT (매도 완료)
        LONG -> PENDING (매도 주문 중)
        PENDING -> FLAT (주문 취소 또는 실패)
        PENDING -> LONG (매수 주문 완료)
        """
        valid_transitions = {
            PositionState.FLAT: [PositionState.LONG, PositionState.PENDING],
            PositionState.LONG: [PositionState.FLAT, PositionState.PENDING],
            PositionState.PENDING: [PositionState.FLAT, PositionState.LONG],
        }
        
        return to_state in valid_transitions.get(from_state, [])
    
    def get_state(self) -> PositionState:
        """현재 상태 반환"""
        return self.state
    
    def is_flat(self) -> bool:
        """FLAT 상태인지 확인"""
        return self.state == PositionState.FLAT
    
    def is_long(self) -> bool:
        """LONG 상태인지 확인"""
        return self.state == PositionState.LONG
    
    def is_pending(self) -> bool:
        """PENDING 상태인지 확인"""
        return self.state == PositionState.PENDING
    
    def set_position(self, position: dict):
        """현재 포지션 설정"""
        self.current_position = position
    
    def clear_position(self):
        """현재 포지션 제거"""
        self.current_position = None
    
    def get_position(self) -> Optional[dict]:
        """현재 포지션 반환"""
        return self.current_position

