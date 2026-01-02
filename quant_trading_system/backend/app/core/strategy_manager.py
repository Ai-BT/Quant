"""
전략 관리 및 자동 재시작 로직
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from app.core.mock_data import mock_store
from app.core.logging import get_logger

logger = get_logger(__name__, "strategy")


class StrategyManager:
    """전략 관리 및 자동 재시작 관리자"""
    
    def __init__(self):
        self.running_strategies: Dict[str, Dict[str, Any]] = {}
        self.strategy_restart_counts: Dict[str, int] = {}
        self.max_restart_attempts = 5
        self.restart_delay_seconds = 60  # 1분
    
    def start_strategy(self, strategy_id: str) -> Dict[str, Any]:
        """전략 시작"""
        # 전략이 실행 중인지 확인
        if strategy_id in self.running_strategies:
            logger.warning(f"Strategy {strategy_id} is already running")
            return self.running_strategies[strategy_id]
        
        # 전략 시작 (mock_store는 선택사항)
        try:
            mock_store.start_strategy(strategy_id)
        except:
            # mock_store에 없어도 계속 진행 (동적으로 로드되는 전략)
            pass
        
        self.running_strategies[strategy_id] = {
            "strategy_id": strategy_id,
            "status": "running",
            "started_at": datetime.now().isoformat(),
            "last_heartbeat": datetime.now().isoformat(),
            "restart_count": 0,
            "error_count": 0,
        }
        self.strategy_restart_counts[strategy_id] = 0
        
        logger.info(f"Strategy {strategy_id} started successfully")
        return self.running_strategies[strategy_id]
    
    def stop_strategy(self, strategy_id: str) -> Dict[str, Any]:
        """전략 중지"""
        # 전략 중지 (mock_store는 선택사항)
        try:
            mock_store.stop_strategy(strategy_id)
        except:
            # mock_store에 없어도 계속 진행
            pass
        
        # running_strategies에서 제거 (있으면)
        strategy_info = self.running_strategies.pop(strategy_id, {})
        self.strategy_restart_counts.pop(strategy_id, None)
        
        logger.info(f"Strategy {strategy_id} stopped successfully")
        return strategy_info
    
    def update_heartbeat(self, strategy_id: str):
        """전략 하트비트 업데이트"""
        if strategy_id in self.running_strategies:
            self.running_strategies[strategy_id]["last_heartbeat"] = datetime.now().isoformat()
    
    def record_error(self, strategy_id: str, error: Exception):
        """전략 에러 기록"""
        if strategy_id in self.running_strategies:
            self.running_strategies[strategy_id]["error_count"] += 1
            self.running_strategies[strategy_id]["last_error"] = {
                "message": str(error),
                "type": type(error).__name__,
                "timestamp": datetime.now().isoformat(),
            }
            logger.error(f"Strategy {strategy_id} error: {error}", exc_info=True)
    
    def should_restart(self, strategy_id: str) -> bool:
        """전략 재시작 여부 판단"""
        if strategy_id not in self.running_strategies:
            return False
        
        restart_count = self.strategy_restart_counts.get(strategy_id, 0)
        if restart_count >= self.max_restart_attempts:
            logger.error(f"Strategy {strategy_id} exceeded max restart attempts ({self.max_restart_attempts})")
            return False
        
        # 하트비트 확인 (5분 이상 응답 없으면 재시작)
        strategy_info = self.running_strategies.get(strategy_id)
        if strategy_info:
            last_heartbeat = datetime.fromisoformat(strategy_info["last_heartbeat"])
            if (datetime.now() - last_heartbeat).total_seconds() > 300:  # 5분
                logger.warning(f"Strategy {strategy_id} heartbeat timeout, will restart")
                return True
        
        return False
    
    async def auto_restart_strategy(self, strategy_id: str):
        """전략 자동 재시작"""
        if strategy_id not in self.running_strategies:
            return
        
        restart_count = self.strategy_restart_counts.get(strategy_id, 0)
        if restart_count >= self.max_restart_attempts:
            logger.error(f"Strategy {strategy_id} exceeded max restart attempts, stopping")
            self.stop_strategy(strategy_id)
            return
        
        logger.info(f"Restarting strategy {strategy_id} (attempt {restart_count + 1}/{self.max_restart_attempts})")
        
        # 재시작 전 대기
        await asyncio.sleep(self.restart_delay_seconds)
        
        try:
            # 전략 재시작
            self.strategy_restart_counts[strategy_id] = restart_count + 1
            strategy_info = self.start_strategy(strategy_id)
            strategy_info["restart_count"] = self.strategy_restart_counts[strategy_id]
            
            logger.info(f"Strategy {strategy_id} restarted successfully")
        except Exception as e:
            logger.error(f"Failed to restart strategy {strategy_id}: {e}")
            self.record_error(strategy_id, e)
    
    def get_running_strategies(self) -> List[Dict[str, Any]]:
        """실행 중인 전략 목록"""
        return list(self.running_strategies.values())
    
    def get_strategy_status(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        """전략 상태 조회"""
        return self.running_strategies.get(strategy_id)
    
    def check_all_strategies(self):
        """모든 전략 상태 확인 및 자동 재시작"""
        for strategy_id in list(self.running_strategies.keys()):
            if self.should_restart(strategy_id):
                asyncio.create_task(self.auto_restart_strategy(strategy_id))


# 전역 전략 관리자 인스턴스
strategy_manager = StrategyManager()

