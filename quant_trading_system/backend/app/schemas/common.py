from pydantic import BaseModel
from typing import Optional, Dict, Any


class HealthResponse(BaseModel):
    """서버 상태 응답"""
    status: str
    uptime_seconds: int
    started_at: str
    version: str


class MessageResponse(BaseModel):
    """일반 메시지 응답"""
    message: str
    details: Optional[Dict[str, Any]] = None



