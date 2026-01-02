"""
거래 내역 조회 API
"""
from fastapi import APIRouter, HTTPException, Query
from app.schemas.trade import TradeResponse, TradeListResponse
from app.core.mock_data import mock_store

router = APIRouter(prefix="/trades", tags=["Trades"])


@router.get("/", response_model=TradeListResponse)
async def get_trades(
    limit: int = Query(20, ge=1, le=100, description="조회할 개수"),
    offset: int = Query(0, ge=0, description="시작 위치"),
):
    """최근 거래 내역 조회"""
    trades = mock_store.get_trades(limit=limit, offset=offset)
    all_trades = mock_store.get_trades(limit=1000, offset=0)  # 전체 개수 계산용
    
    return TradeListResponse(
        trades=[TradeResponse(**trade) for trade in trades],
        total=len(all_trades),
        limit=limit,
        offset=offset,
    )


@router.get("/{trade_id}", response_model=TradeResponse)
async def get_trade(trade_id: str):
    """특정 거래 내역 조회"""
    trade = mock_store.get_trade(trade_id)
    if not trade:
        raise HTTPException(status_code=404, detail=f"Trade {trade_id} not found")
    return TradeResponse(**trade)



