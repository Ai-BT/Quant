"""
전략 베이스 클래스

실시간 실행 가능한 전략의 기본 인터페이스
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.core.virtual_account import VirtualAccount


class BaseStrategy(ABC):
    """전략 베이스 클래스"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Parameters
        ----------
        config : Dict[str, Any], optional
            전략 설정
        """
        self.config = config or {}
        self.market = self.config.get('market', 'KRW-SOL')
        self.name = self.config.get('name', self.__class__.__name__)
    
    @abstractmethod
    async def initialize(self, account: VirtualAccount, upbit_adapter=None):
        """
        전략 초기화
        
        Parameters
        ----------
        account : VirtualAccount
            가상 계좌 인스턴스
        upbit_adapter : UpbitAdapter, optional
            Upbit API 어댑터 (과거 데이터 로드용)
        """
        pass
    
    @abstractmethod
    async def execute(self, account: VirtualAccount, current_price: float, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        전략 실행 (매 사이클마다 호출)
        
        Parameters
        ----------
        account : VirtualAccount
            가상 계좌 인스턴스
        current_price : float
            현재가
        market_data : Dict[str, Any]
            시장 데이터 (캔들 데이터 등)
        
        Returns
        -------
        Dict[str, Any]
            실행 결과
            - signal: 'BUY', 'SELL', 'HOLD'
            - message: 실행 메시지
        """
        pass
    
    @abstractmethod
    async def cleanup(self, account: VirtualAccount):
        """
        전략 종료 시 정리 작업
        
        Parameters
        ----------
        account : VirtualAccount
            가상 계좌 인스턴스
        """
        pass

