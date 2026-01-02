"""
전략 베이스 클래스
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from app.data.candle import Candle, Timeframe
from app.core.state_machine import PositionState


class BaseStrategy(ABC):
    """전략 베이스 클래스"""
    
    def __init__(self, name: str):
        """
        초기화
        
        Parameters
        ----------
        name : str
            전략 이름
        """
        self.name = name
    
    @abstractmethod
    def generate_signal(self, candles: Dict[Timeframe, List[Candle]], 
                       current_state: PositionState,
                       features: Optional[Dict] = None) -> Dict:
        """
        시그널 생성
        
        Parameters
        ----------
        candles : Dict[Timeframe, List[Candle]]
            타임프레임별 캔들 데이터
        current_state : PositionState
            현재 포지션 상태
        features : Dict, optional
            계산된 피처들
        
        Returns
        -------
        dict
            {
                'action': 'BUY' | 'SELL' | 'HOLD',
                'confidence': float,  # 0.0 ~ 1.0
                'reason': str,
                'metadata': dict
            }
        """
        pass
    
    def get_required_timeframes(self) -> List[Timeframe]:
        """
        필요한 타임프레임 리스트 반환
        
        Returns
        -------
        List[Timeframe]
            필요한 타임프레임 리스트
        """
        return [Timeframe.MIN_15, Timeframe.HOUR_1]  # 기본값

