"""
캔들 데이터 모델 및 관리
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum


class Timeframe(Enum):
    """타임프레임"""
    MIN_1 = "1m"
    MIN_5 = "5m"
    MIN_15 = "15m"
    MIN_30 = "30m"
    HOUR_1 = "1h"
    HOUR_4 = "4h"
    DAY_1 = "1d"


@dataclass
class Candle:
    """캔들 데이터"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    
    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume
        }


class CandleStore:
    """캔들 데이터 저장소"""
    
    def __init__(self):
        self._candles: dict[str, List[Candle]] = {}  # key: "symbol_timeframe"
    
    def add_candle(self, symbol: str, timeframe: Timeframe, candle: Candle):
        """캔들 추가"""
        key = f"{symbol}_{timeframe.value}"
        if key not in self._candles:
            self._candles[key] = []
        
        self._candles[key].append(candle)
        # 시간순 정렬
        self._candles[key].sort(key=lambda x: x.timestamp)
    
    def get_candles(self, symbol: str, timeframe: Timeframe, 
                   limit: Optional[int] = None) -> List[Candle]:
        """
        캔들 조회
        
        Parameters
        ----------
        symbol : str
            심볼 (예: "KRW-BTC")
        timeframe : Timeframe
            타임프레임
        limit : int, optional
            최대 개수 (None이면 전체)
        
        Returns
        -------
        List[Candle]
            캔들 리스트 (오래된 것부터 최신 순)
        """
        key = f"{symbol}_{timeframe.value}"
        candles = self._candles.get(key, [])
        
        if limit:
            return candles[-limit:]
        return candles
    
    def get_latest_candle(self, symbol: str, timeframe: Timeframe) -> Optional[Candle]:
        """최신 캔들 조회"""
        candles = self.get_candles(symbol, timeframe)
        return candles[-1] if candles else None
    
    def is_candle_closed(self, symbol: str, timeframe: Timeframe, 
                        current_time: datetime) -> bool:
        """
        캔들이 마감되었는지 확인
        
        간단한 구현: 실제로는 거래소 API나 데이터 소스에서 확인해야 함
        """
        latest = self.get_latest_candle(symbol, timeframe)
        if not latest:
            return False
        
        # 타임프레임에 따른 마감 시간 계산
        # 실제 구현에서는 타임프레임에 맞는 마감 시간을 정확히 계산해야 함
        return True

