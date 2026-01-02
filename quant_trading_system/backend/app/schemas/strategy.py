from pydantic import BaseModel
from typing import Optional


class StrategyResponse(BaseModel):
    """전략 응답"""
    id: str
    name: str
    type: str  # traditional, ai, hybrid
    market: str
    status: str  # running, stopped
    created_at: str
    updated_at: str


class StrategyStartRequest(BaseModel):
    """전략 시작 요청"""
    strategy_id: str


class StrategyStopRequest(BaseModel):
    """전략 중지 요청"""
    strategy_id: str


