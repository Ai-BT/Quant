from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class LogResponse(BaseModel):
    """로그 응답"""
    id: str
    level: str  # INFO, WARNING, ERROR, DEBUG
    type: str  # strategy, order, system
    message: str
    details: Dict[str, Any]
    created_at: str


class LogListResponse(BaseModel):
    """로그 목록 응답"""
    logs: List[LogResponse]
    total: int
    limit: int
    offset: int



