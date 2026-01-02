"""
가상 계좌 관리자

전략별로 독립적인 가상 계좌를 생성하고 관리
"""
from typing import Dict, Optional
from app.core.virtual_account import VirtualAccount
from app.core.logging import get_logger

logger = get_logger(__name__, "virtual_account_manager")


class VirtualAccountManager:
    """가상 계좌 관리자"""
    
    def __init__(self, initial_balance_per_strategy: float = 5_000_000):
        """
        Parameters
        ----------
        initial_balance_per_strategy : float
            전략당 초기 자금 (기본 500만원)
        """
        self.initial_balance_per_strategy = initial_balance_per_strategy
        self.accounts: Dict[str, VirtualAccount] = {}
        self._default_account: Optional[VirtualAccount] = None
    
    def get_account(self, strategy_id: str) -> VirtualAccount:
        """
        전략별 계좌 가져오기 (없으면 생성)
        
        Parameters
        ----------
        strategy_id : str
            전략 ID
        
        Returns
        -------
        VirtualAccount
            해당 전략의 가상 계좌
        """
        if strategy_id not in self.accounts:
            logger.info(f"전략별 계좌 생성: {strategy_id} (초기 자금: {self.initial_balance_per_strategy:,.0f}원)")
            self.accounts[strategy_id] = VirtualAccount(initial_balance=self.initial_balance_per_strategy)
        
        return self.accounts[strategy_id]
    
    def remove_account(self, strategy_id: str):
        """
        전략 계좌 제거
        
        Parameters
        ----------
        strategy_id : str
            전략 ID
        """
        if strategy_id in self.accounts:
            del self.accounts[strategy_id]
            logger.info(f"전략별 계좌 제거: {strategy_id}")
    
    def get_default_account(self) -> VirtualAccount:
        """
        기본 계좌 가져오기 (전략과 연결되지 않은 용도)
        
        Returns
        -------
        VirtualAccount
            기본 가상 계좌
        """
        if self._default_account is None:
            self._default_account = VirtualAccount(initial_balance=10_000_000)
        return self._default_account
    
    def get_all_accounts(self) -> Dict[str, VirtualAccount]:
        """
        모든 전략 계좌 가져오기
        
        Returns
        -------
        Dict[str, VirtualAccount]
            전략 ID별 계좌 딕셔너리
        """
        return self.accounts.copy()


# 전역 가상 계좌 관리자 인스턴스
# 전략당 500만원씩 할당
virtual_account_manager = VirtualAccountManager(initial_balance_per_strategy=5_000_000)


