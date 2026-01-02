from pydantic import BaseModel
from typing import List, Optional


class TradeResponse(BaseModel):
    """거래 내역 응답"""
    id: str
    market: str
    side: str  # bid (매수), ask (매도)
    price: float
    volume: float
    amount: float
    fee: float
    strategy_id: Optional[str] = None
    status: str
    created_at: str


class TradeListResponse(BaseModel):
    """거래 내역 목록 응답"""
    trades: List[TradeResponse]
    total: int
    limit: int
    offset: int


