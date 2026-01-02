from pydantic import BaseModel
from typing import List


class PositionResponse(BaseModel):
    """포지션 응답"""
    market: str
    currency: str
    balance: float
    avg_buy_price: float
    current_price: float
    profit_loss: float
    profit_loss_rate: float
    updated_at: str


class PositionListResponse(BaseModel):
    """포지션 목록 응답"""
    positions: List[PositionResponse]
    total: int


