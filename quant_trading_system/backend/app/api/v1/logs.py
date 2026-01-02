"""
로그 조회 API
"""
from fastapi import APIRouter, Query
from app.schemas.log import LogResponse, LogListResponse
from app.core.mock_data import mock_store

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.get("/", response_model=LogListResponse)
async def get_logs(
    level: str | None = Query(None, description="로그 레벨 (INFO, WARNING, ERROR, DEBUG)"),
    type: str | None = Query(None, description="로그 타입 (strategy, order, system)"),
    limit: int = Query(50, ge=1, le=200, description="조회할 개수"),
    offset: int = Query(0, ge=0, description="시작 위치"),
):
    """로그 조회"""
    logs = mock_store.get_logs(level=level, log_type=type, limit=limit, offset=offset)
    all_logs = mock_store.get_logs(level=level, log_type=type, limit=10000, offset=0)  # 전체 개수 계산용
    
    return LogListResponse(
        logs=[LogResponse(**log) for log in logs],
        total=len(all_logs),
        limit=limit,
        offset=offset,
    )


