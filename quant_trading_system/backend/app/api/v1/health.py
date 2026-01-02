"""
서버 상태 확인 API
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, List
from app.schemas.common import HealthResponse
from app.core.config import settings
from app.core.mock_data import mock_store
from app.core.monitoring import system_monitor
from app.core.strategy_manager import strategy_manager
from app.core.job_state import job_state_manager

router = APIRouter(tags=["Health"])


class DetailedHealthResponse(BaseModel):
    """상세 헬스 체크 응답"""
    status: str
    version: str
    uptime: Dict[str, Any]
    system: Dict[str, Any]
    strategies: Dict[str, Any]
    jobs: Dict[str, Any]


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """서버 상태 확인 (기본)"""
    status = mock_store.get_server_status()
    return HealthResponse(
        status=status["status"],
        uptime_seconds=status["uptime_seconds"],
        started_at=status["started_at"],
        version=settings.api_version,
    )


@router.get("/health/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check():
    """상세 서버 상태 확인"""
    # 시스템 메트릭
    metrics = system_monitor.get_all_metrics()
    
    # 전략 상태
    running_strategies = strategy_manager.get_running_strategies()
    strategy_status = {
        "total_running": len(running_strategies),
        "strategies": running_strategies,
    }
    
    # 작업 상태
    all_jobs = job_state_manager.get_all_states()
    job_status = {
        "total": len(all_jobs),
        "running": len([j for j in all_jobs if j.get("status") == "running"]),
        "paused": len([j for j in all_jobs if j.get("status") == "paused"]),
        "failed": len([j for j in all_jobs if j.get("status") == "failed"]),
    }
    
    # 전체 상태 판단
    overall_status = "healthy"
    if metrics.get("memory", {}).get("system", {}).get("percent", 0) > 90:
        overall_status = "degraded"
    if metrics.get("disk", {}).get("percent", 0) > 90:
        overall_status = "degraded"
    if job_status["failed"] > 0:
        overall_status = "degraded"
    
    return DetailedHealthResponse(
        status=overall_status,
        version=settings.api_version,
        uptime=metrics.get("uptime", {}),
        system=metrics,
        strategies=strategy_status,
        jobs=job_status,
    )


@router.get("/health/metrics")
async def metrics():
    """시스템 메트릭 조회"""
    return system_monitor.get_all_metrics()

