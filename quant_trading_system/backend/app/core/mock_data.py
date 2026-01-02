"""
Mock 데이터 저장소
실제 거래소 연결 전까지 사용할 Mock 데이터
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random


class MockDataStore:
    """Mock 데이터 저장소"""
    
    def __init__(self):
        self._strategies: Dict[str, Dict[str, Any]] = {}
        self._positions: Dict[str, Dict[str, Any]] = {}
        self._trades: List[Dict[str, Any]] = []
        self._logs: List[Dict[str, Any]] = []
        self._server_status = {
            "status": "healthy",
            "uptime_seconds": 0,
            "started_at": datetime.now().isoformat(),
        }
        
        # 초기 Mock 데이터 생성
        self._initialize_mock_data()
    
    def _initialize_mock_data(self):
        """초기 Mock 데이터 생성"""
        # 초기 전략 데이터
        self._strategies = {
            "strategy_1": {
                "id": "strategy_1",
                "name": "SMA 크로스오버 전략",
                "type": "traditional",
                "market": "KRW-BTC",
                "status": "stopped",
                "created_at": (datetime.now() - timedelta(days=5)).isoformat(),
                "updated_at": datetime.now().isoformat(),
            },
            "strategy_2": {
                "id": "strategy_2",
                "name": "LSTM 예측 전략",
                "type": "ai",
                "market": "KRW-ETH",
                "status": "running",
                "created_at": (datetime.now() - timedelta(days=3)).isoformat(),
                "updated_at": datetime.now().isoformat(),
            },
        }
        
        # 초기 포지션 데이터
        self._positions = {
            "KRW-BTC": {
                "market": "KRW-BTC",
                "currency": "BTC",
                "balance": 0.05,
                "avg_buy_price": 85000000,
                "current_price": 87000000,
                "profit_loss": 1000000,
                "profit_loss_rate": 2.35,
                "updated_at": datetime.now().isoformat(),
            },
            "KRW-ETH": {
                "market": "KRW-ETH",
                "currency": "ETH",
                "balance": 2.5,
                "avg_buy_price": 3200000,
                "current_price": 3150000,
                "profit_loss": -12500,
                "profit_loss_rate": -0.39,
                "updated_at": datetime.now().isoformat(),
            },
        }
        
        # 초기 거래 내역
        base_time = datetime.now() - timedelta(hours=24)
        markets = ["KRW-BTC", "KRW-ETH", "KRW-SOL"]
        sides = ["bid", "ask"]
        
        for i in range(20):
            market = random.choice(markets)
            side = random.choice(sides)
            price = random.randint(50000000, 100000000) if "BTC" in market else random.randint(2000000, 5000000)
            volume = round(random.uniform(0.001, 0.1), 6)
            
            self._trades.append({
                "id": f"trade_{i+1}",
                "market": market,
                "side": side,
                "price": price,
                "volume": volume,
                "amount": price * volume,
                "fee": round(price * volume * 0.0005, 2),
                "strategy_id": f"strategy_{random.randint(1, 2)}",
                "status": "done",
                "created_at": (base_time + timedelta(hours=i)).isoformat(),
            })
        
        # 초기 로그 데이터
        log_levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
        log_types = ["strategy", "order", "system"]
        
        for i in range(50):
            self._logs.append({
                "id": f"log_{i+1}",
                "level": random.choice(log_levels),
                "type": random.choice(log_types),
                "message": f"Mock log message {i+1}",
                "details": {"key": f"value_{i+1}"},
                "created_at": (base_time + timedelta(minutes=i*30)).isoformat(),
            })
    
    # 전략 관련 메서드
    def get_strategies(self) -> List[Dict[str, Any]]:
        """전략 목록 조회"""
        return list(self._strategies.values())
    
    def get_strategy(self, strategy_id: str) -> Dict[str, Any] | None:
        """전략 조회"""
        return self._strategies.get(strategy_id)
    
    def start_strategy(self, strategy_id: str) -> Dict[str, Any] | None:
        """전략 시작"""
        if strategy_id not in self._strategies:
            return None
        
        strategy = self._strategies[strategy_id]
        strategy["status"] = "running"
        strategy["updated_at"] = datetime.now().isoformat()
        
        # 로그 추가
        self._logs.append({
            "id": f"log_{len(self._logs)+1}",
            "level": "INFO",
            "type": "strategy",
            "message": f"Strategy {strategy_id} started",
            "details": {"strategy_id": strategy_id, "strategy_name": strategy["name"]},
            "created_at": datetime.now().isoformat(),
        })
        
        return strategy
    
    def stop_strategy(self, strategy_id: str) -> Dict[str, Any] | None:
        """전략 중지"""
        if strategy_id not in self._strategies:
            return None
        
        strategy = self._strategies[strategy_id]
        strategy["status"] = "stopped"
        strategy["updated_at"] = datetime.now().isoformat()
        
        # 로그 추가
        self._logs.append({
            "id": f"log_{len(self._logs)+1}",
            "level": "INFO",
            "type": "strategy",
            "message": f"Strategy {strategy_id} stopped",
            "details": {"strategy_id": strategy_id, "strategy_name": strategy["name"]},
            "created_at": datetime.now().isoformat(),
        })
        
        return strategy
    
    # 포지션 관련 메서드
    def get_positions(self) -> List[Dict[str, Any]]:
        """포지션 목록 조회"""
        return list(self._positions.values())
    
    def get_position(self, market: str) -> Dict[str, Any] | None:
        """특정 마켓 포지션 조회"""
        return self._positions.get(market)
    
    # 거래 내역 관련 메서드
    def get_trades(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """거래 내역 조회"""
        sorted_trades = sorted(self._trades, key=lambda x: x["created_at"], reverse=True)
        return sorted_trades[offset:offset+limit]
    
    def get_trade(self, trade_id: str) -> Dict[str, Any] | None:
        """특정 거래 조회"""
        for trade in self._trades:
            if trade["id"] == trade_id:
                return trade
        return None
    
    # 로그 관련 메서드
    def get_logs(
        self,
        level: str | None = None,
        log_type: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """로그 조회"""
        filtered_logs = self._logs
        
        if level:
            filtered_logs = [log for log in filtered_logs if log["level"] == level]
        
        if log_type:
            filtered_logs = [log for log in filtered_logs if log["type"] == log_type]
        
        sorted_logs = sorted(filtered_logs, key=lambda x: x["created_at"], reverse=True)
        return sorted_logs[offset:offset+limit]
    
    def add_log(self, level: str, log_type: str, message: str, details: Dict[str, Any] | None = None):
        """로그 추가"""
        self._logs.append({
            "id": f"log_{len(self._logs)+1}",
            "level": level,
            "type": log_type,
            "message": message,
            "details": details or {},
            "created_at": datetime.now().isoformat(),
        })
    
    # 서버 상태 관련 메서드
    def get_server_status(self) -> Dict[str, Any]:
        """서버 상태 조회"""
        started_at = datetime.fromisoformat(self._server_status["started_at"])
        uptime_seconds = int((datetime.now() - started_at).total_seconds())
        self._server_status["uptime_seconds"] = uptime_seconds
        return self._server_status


# 전역 Mock 데이터 저장소 인스턴스
mock_store = MockDataStore()

