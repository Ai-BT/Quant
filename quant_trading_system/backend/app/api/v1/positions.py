"""
포지션 조회 API
"""
from fastapi import APIRouter, HTTPException
from app.schemas.position import PositionResponse, PositionListResponse
from app.core.mock_data import mock_store

router = APIRouter(prefix="/positions", tags=["Positions"])


@router.get("/", response_model=PositionListResponse)
async def get_positions():
    """현재 포지션 목록 조회"""
    positions = mock_store.get_positions()
    return PositionListResponse(
        positions=[PositionResponse(**position) for position in positions],
        total=len(positions),
    )


@router.get("/{market}", response_model=PositionResponse)
async def get_position(market: str):
    """특정 마켓 포지션 조회"""
    position = mock_store.get_position(market)
    if not position:
        raise HTTPException(status_code=404, detail=f"Position for {market} not found")
    return PositionResponse(**position)


