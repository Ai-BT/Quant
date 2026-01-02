"""
모니터링 API
프로세스 상태, 전략 상태, 작업 상태 조회
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
from app.core.monitoring import system_monitor
from app.core.strategy_manager import strategy_manager
from app.core.job_state import job_state_manager

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


class StrategyStatusResponse(BaseModel):
    """전략 상태 응답"""
    strategy_id: str
    status: str
    started_at: str
    last_heartbeat: str
    restart_count: int
    error_count: int
    last_error: Dict[str, Any] | None = None


class JobStatusResponse(BaseModel):
    """작업 상태 응답"""
    job_id: str
    status: str
    created_at: str
    updated_at: str
    details: Dict[str, Any] | None = None


@router.get("/strategies")
async def get_strategy_statuses():
    """실행 중인 전략 상태 조회"""
    strategies = strategy_manager.get_running_strategies()
    return {
        "total": len(strategies),
        "strategies": [StrategyStatusResponse(**s) for s in strategies],
    }


@router.get("/strategies/{strategy_id}")
async def get_strategy_status(strategy_id: str):
    """특정 전략 상태 조회"""
    status = strategy_manager.get_strategy_status(strategy_id)
    if not status:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Strategy {strategy_id} not found")
    return StrategyStatusResponse(**status)


@router.get("/jobs")
async def get_job_statuses(status: str | None = None):
    """작업 상태 조회"""
    jobs = job_state_manager.get_all_states(status=status)
    return {
        "total": len(jobs),
        "jobs": [JobStatusResponse(**j) for j in jobs],
    }


@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """특정 작업 상태 조회"""
    status = job_state_manager.get_state(job_id)
    if not status:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return JobStatusResponse(**status)


@router.post("/jobs/{job_id}/resume")
async def resume_job(job_id: str):
    """작업 재개"""
    job = job_state_manager.resume_job(job_id)
    if not job:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found or cannot be resumed")
    return JobStatusResponse(**job)


@router.get("/system")
async def get_system_metrics():
    """시스템 메트릭 조회"""
    return system_monitor.get_all_metrics()


