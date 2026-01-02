"""
전략 관리 API
"""
from fastapi import APIRouter, HTTPException
from app.schemas.strategy import (
    StrategyResponse,
    StrategyStartRequest,
    StrategyStopRequest,
)
from app.schemas.common import MessageResponse
from app.core.mock_data import mock_store
from app.core.strategy_manager import strategy_manager
from app.core.strategy_loader import strategy_loader
from app.core.logging import get_logger

logger = get_logger(__name__, "strategy")
router = APIRouter(prefix="/strategies", tags=["Strategies"])


@router.get("/", response_model=list[StrategyResponse])
async def get_strategies():
    """전략 목록 조회"""
    # 실제 전략 폴더에서 전략 목록 조회
    try:
        discovered_strategies = strategy_loader.discover_strategies()
        strategies_list = []
        
        for strategy_name in discovered_strategies:
            try:
                strategy_info = strategy_loader.get_strategy_info(strategy_name)
                # Mock 데이터와 유사한 형태로 변환
                strategy_data = {
                    'id': strategy_name,
                    'name': strategy_name.replace('_', ' ').title(),
                    'type': 'traditional',  # 기본값, 추후 전략에서 가져올 수 있음
                    'market': 'KRW-BTC',  # 기본값
                    'status': 'stopped',
                    'created_at': '2025-01-01T00:00:00',
                    'updated_at': '2025-01-01T00:00:00',
                }
                
                # config에서 정보 가져오기
                if 'config' in strategy_info:
                    config = strategy_info['config']
                    if 'STRATEGY_CONFIG' in config:
                        strategy_config = config['STRATEGY_CONFIG']
                        if 'name' in strategy_config:
                            strategy_data['name'] = strategy_config['name']
                        if 'market' in strategy_config:
                            strategy_data['market'] = strategy_config.get('market', 'KRW-BTC')
                    else:
                        # 직접 config에 있는 경우
                        if 'name' in config:
                            strategy_data['name'] = config['name']
                        if 'market' in config:
                            strategy_data['market'] = config.get('market', 'KRW-BTC')
                
                # 전략 실행 상태 확인
                from app.core.strategy_executor import strategy_executor
                if strategy_executor.is_running(strategy_name):
                    strategy_data['status'] = 'running'
                
                strategies_list.append(strategy_data)
            except Exception as e:
                logger.warning(f"전략 정보 조회 실패: {strategy_name}, 오류: {e}")
                continue
        
        # 발견된 전략이 없으면 Mock 데이터 사용
        if not strategies_list:
            strategies = mock_store.get_strategies()
            return [StrategyResponse(**strategy) for strategy in strategies]
        
        return [StrategyResponse(**strategy) for strategy in strategies_list]
        
    except Exception as e:
        logger.error(f"전략 목록 조회 실패: {e}", exc_info=True)
        # 에러 시 Mock 데이터 사용
        strategies = mock_store.get_strategies()
        return [StrategyResponse(**strategy) for strategy in strategies]


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(strategy_id: str):
    """전략 상세 조회"""
    strategy = mock_store.get_strategy(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail=f"Strategy {strategy_id} not found")
    return StrategyResponse(**strategy)


@router.post("/{strategy_id}/start", response_model=MessageResponse)
async def start_strategy(strategy_id: str):
    """전략 시작"""
    try:
        # 전략 실행기 사용
        from app.core.strategy_executor import strategy_executor
        
        # 전략 정보 조회 (설정 포함)
        strategy_info = strategy_loader.get_strategy_info(strategy_id)
        config_dict = strategy_info.get('config', {})
        # STRATEGY_CONFIG 또는 직접 config 딕셔너리 사용
        config = config_dict.get('STRATEGY_CONFIG', config_dict)
        
        # Strategy Manager에 등록
        strategy_info_manager = strategy_manager.start_strategy(strategy_id)
        
        # 전략 실행 시작
        try:
            # 전략 클래스 로드
            strategy_class = strategy_loader.load_strategy(strategy_id)
            result = await strategy_executor.start_strategy(strategy_id, config)
        except Exception as executor_error:
            # 실행 실패 시 Strategy Manager에서 제거
            strategy_manager.stop_strategy(strategy_id)
            raise executor_error
        
        # 작업 상태 저장
        from app.core.job_state import job_state_manager
        job_state_manager.update_state(
            f"strategy_{strategy_id}",
            {
                "job_type": "strategy",
                "strategy_id": strategy_id,
                "status": "running",
            }
        )
        
        # 전략 정보 가져오기 (mock_store가 아닌 strategy_loader에서)
        strategy_info = strategy_loader.get_strategy_info(strategy_id)
        config_dict = strategy_info.get('config', {})
        config = config_dict.get('STRATEGY_CONFIG', config_dict)
        
        strategy_data = {
            'id': strategy_id,
            'name': config.get('name', strategy_id.replace('_', ' ').title()),
            'type': 'traditional',
            'market': config.get('market', 'KRW-BTC'),
            'status': 'running',
            'created_at': '2025-01-01T00:00:00',
            'updated_at': __import__("datetime").datetime.now().isoformat(),
        }
        
        return MessageResponse(
            message=f"Strategy {strategy_id} started successfully",
            details={
                "strategy": StrategyResponse(**strategy_data).model_dump(),
                "manager_info": strategy_info_manager,
                "executor_result": result,
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to start strategy {strategy_id}: {e}", exc_info=True)
        strategy_manager.record_error(strategy_id, e)
        raise HTTPException(status_code=500, detail=f"Failed to start strategy: {str(e)}")


@router.post("/{strategy_id}/stop", response_model=MessageResponse)
async def stop_strategy(strategy_id: str):
    """전략 중지"""
    try:
        # 전략 실행기 사용
        from app.core.strategy_executor import strategy_executor
        
        # 전략 실행 중지
        executor_result = await strategy_executor.stop_strategy(strategy_id)
        
        # Strategy Manager를 통한 중지
        strategy_info = strategy_manager.stop_strategy(strategy_id)
        
        # 작업 상태 업데이트
        from app.core.job_state import job_state_manager
        job_state_manager.update_state(
            f"strategy_{strategy_id}",
            {
                "status": "stopped",
                "stopped_at": __import__("datetime").datetime.now().isoformat(),
            }
        )
        
        # 전략 정보 가져오기 (mock_store가 아닌 strategy_loader에서)
        try:
            strategy_info_data = strategy_loader.get_strategy_info(strategy_id)
            config_dict = strategy_info_data.get('config', {})
            config = config_dict.get('STRATEGY_CONFIG', config_dict)
            
            strategy_data = {
                'id': strategy_id,
                'name': config.get('name', strategy_id.replace('_', ' ').title()),
                'type': 'traditional',
                'market': config.get('market', 'KRW-BTC'),
                'status': 'stopped',
                'created_at': '2025-01-01T00:00:00',
                'updated_at': __import__("datetime").datetime.now().isoformat(),
            }
        except Exception as e:
            # 전략 정보를 가져올 수 없으면 기본값 사용
            logger.warning(f"전략 정보 조회 실패: {strategy_id}, 오류: {e}")
            strategy_data = {
                'id': strategy_id,
                'name': strategy_id.replace('_', ' ').title(),
                'type': 'traditional',
                'market': 'KRW-BTC',
                'status': 'stopped',
                'created_at': '2025-01-01T00:00:00',
                'updated_at': __import__("datetime").datetime.now().isoformat(),
            }
        
        return MessageResponse(
            message=f"Strategy {strategy_id} stopped successfully",
            details={
                "strategy": StrategyResponse(**strategy_data).model_dump(),
                "manager_info": strategy_info,
                "executor_result": executor_result,
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to stop strategy {strategy_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to stop strategy: {str(e)}")

