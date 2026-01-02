"""
전략 실행 엔진

가상 계좌를 사용하여 전략을 실행하는 엔진
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from app.core.strategy_loader import strategy_loader
from app.core.virtual_account_manager import virtual_account_manager
from app.core.logging import get_logger
from app.core.strategy_manager import strategy_manager
from app.adapters.upbit.adapter import UpbitAdapter
from app.core.config import settings

logger = get_logger(__name__, "strategy_executor")


class StrategyExecutor:
    """전략 실행기"""
    
    def __init__(self):
        self.running_tasks: Dict[str, asyncio.Task] = {}
    
    async def start_strategy(self, strategy_id: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        전략 시작
        
        Parameters
        ----------
        strategy_id : str
            전략 ID (전략 이름)
        config : Dict[str, Any], optional
            전략 설정
        
        Returns
        -------
        Dict[str, Any]
            실행 정보
        """
        if strategy_id in self.running_tasks:
            logger.warning(f"전략이 이미 실행 중입니다: {strategy_id}")
            return {'status': 'already_running', 'strategy_id': strategy_id}
        
        try:
            # 전략 로드
            strategy_class = strategy_loader.load_strategy(strategy_id)
            
            # Strategy Manager에 등록 (이미 API에서 등록했으므로 중복 방지)
            # strategy_manager.start_strategy(strategy_id)  # API에서 이미 호출됨
            
            # 비동기 작업 시작
            task = asyncio.create_task(self._run_strategy(strategy_id, strategy_class, config))
            self.running_tasks[strategy_id] = task
            
            logger.info(f"전략 시작: {strategy_id}")
            return {
                'status': 'started',
                'strategy_id': strategy_id,
                'started_at': datetime.now().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"전략 시작 실패: {strategy_id}, 오류: {e}", exc_info=True)
            raise
    
    async def stop_strategy(self, strategy_id: str) -> Dict[str, Any]:
        """
        전략 중지
        
        Parameters
        ----------
        strategy_id : str
            전략 ID
        
        Returns
        -------
        Dict[str, Any]
            중지 정보
        """
        if strategy_id not in self.running_tasks:
            logger.warning(f"실행 중인 전략이 아닙니다: {strategy_id}")
            return {'status': 'not_running', 'strategy_id': strategy_id}
        
        try:
            # 작업 취소
            task = self.running_tasks[strategy_id]
            task.cancel()
            
            try:
                await task
            except asyncio.CancelledError:
                pass
            
            # 작업 제거
            del self.running_tasks[strategy_id]
            
            # Strategy Manager에서 중지
            strategy_manager.stop_strategy(strategy_id)
            
            logger.info(f"전략 중지: {strategy_id}")
            return {
                'status': 'stopped',
                'strategy_id': strategy_id,
                'stopped_at': datetime.now().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"전략 중지 실패: {strategy_id}, 오류: {e}", exc_info=True)
            raise
    
    async def _run_strategy(self, strategy_id: str, strategy_class: Any, config: Optional[Dict[str, Any]] = None):
        """
        전략 실행 루프
        
        Parameters
        ----------
        strategy_id : str
            전략 ID
        strategy_class : Any
            전략 클래스
        config : Dict[str, Any], optional
            전략 설정
        """
        try:
            # 전략 인스턴스 생성
            strategy_config = config or {}
            strategy_config.setdefault('market', 'KRW-SOL')  # 기본값
            strategy_instance = strategy_class(config=strategy_config)
            
            # UpbitAdapter 생성
            upbit_adapter = None
            if settings.upbit_access_key and settings.upbit_secret_key:
                upbit_adapter = UpbitAdapter(
                    access_key=settings.upbit_access_key,
                    secret_key=settings.upbit_secret_key
                )
            
            # 전략별 계좌 가져오기
            strategy_account = virtual_account_manager.get_account(strategy_id)
            
            # 전략 초기화 (UpbitAdapter 전달하여 과거 데이터 로드 가능하도록)
            if hasattr(strategy_instance, 'initialize'):
                await strategy_instance.initialize(strategy_account, upbit_adapter)
            
            logger.info(f"전략 실행 시작: {strategy_id}, 마켓: {strategy_config.get('market', 'KRW-SOL')}")
            
            # 전략 실행 루프
            market = strategy_config.get('market', 'KRW-SOL')
            check_interval = strategy_config.get('check_interval', 60)  # 기본 1분
            
            while True:
                try:
                    # 하트비트 업데이트
                    strategy_manager.update_heartbeat(strategy_id)
                    
                    # 현재가 조회
                    current_price = 0
                    market_data = {}
                    
                    if upbit_adapter:
                        try:
                            tickers = upbit_adapter.get_ticker([market])
                            if tickers and len(tickers) > 0:
                                ticker = tickers[0]
                                current_price = ticker.get('trade_price', 0)
                                market_data = {
                                    'price': current_price,
                                    'volume': ticker.get('acc_trade_volume_24h', 0),
                                    'change_rate': ticker.get('signed_change_rate', 0),
                                    'high_price': ticker.get('high_price', 0),
                                    'low_price': ticker.get('low_price', 0),
                                }
                        except Exception as e:
                            logger.warning(f"가격 조회 실패: {e}")
                    
                    if current_price > 0:
                        # 전략 실행
                        if hasattr(strategy_instance, 'execute'):
                            result = await strategy_instance.execute(
                                strategy_account,
                                current_price,
                                market_data
                            )
                            
                            signal = result.get('signal', 'HOLD')
                            message = result.get('message', '')
                            
                            if signal != 'HOLD':
                                logger.info(f"[{strategy_id}] {signal}: {message} (현재가: {current_price:,.0f}원)")
                        else:
                            # BaseStrategy 인터페이스를 사용하지 않는 경우
                            # 기존 전략 실행 방식 (향후 확장)
                            pass
                    
                    await asyncio.sleep(check_interval)
                    
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    logger.error(f"전략 실행 중 오류: {strategy_id}, 오류: {e}", exc_info=True)
                    strategy_manager.record_error(strategy_id, e)
                    await asyncio.sleep(check_interval)  # 오류 발생 시 대기 후 재시도
                    
        except asyncio.CancelledError:
            logger.info(f"전략 실행 취소: {strategy_id}")
        except Exception as e:
            logger.error(f"전략 실행 실패: {strategy_id}, 오류: {e}", exc_info=True)
            strategy_manager.record_error(strategy_id, e)
        finally:
            # 정리 작업
            if hasattr(strategy_instance, 'cleanup'):
                try:
                    strategy_account = virtual_account_manager.get_account(strategy_id)
                    await strategy_instance.cleanup(strategy_account)
                except Exception as e:
                    logger.error(f"전략 정리 중 오류: {strategy_id}, 오류: {e}", exc_info=True)
            
            # 전략 계좌는 유지 (전략 중지 후에도 계좌 정보를 확인할 수 있도록)
            # 필요시 계좌도 제거하려면: virtual_account_manager.remove_account(strategy_id)
            
            if strategy_id in self.running_tasks:
                del self.running_tasks[strategy_id]
    
    def get_running_strategies(self) -> List[str]:
        """실행 중인 전략 목록"""
        return list(self.running_tasks.keys())
    
    def is_running(self, strategy_id: str) -> bool:
        """전략 실행 여부 확인"""
        return strategy_id in self.running_tasks


# 전역 전략 실행기 인스턴스
strategy_executor = StrategyExecutor()

