"""
데이터베이스 모델 및 연결 관리
"""
import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import json


class Database:
    """SQLite 데이터베이스 관리"""
    
    def __init__(self, db_path: str = "db/trading.db"):
        """
        데이터베이스 초기화
        
        Parameters
        ----------
        db_path : str
            데이터베이스 파일 경로
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()
    
    def _init_schema(self):
        """데이터베이스 스키마 초기화"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 시그널 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                price REAL NOT NULL,
                features TEXT,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 액션 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                symbol TEXT NOT NULL,
                action_type TEXT NOT NULL,
                order_type TEXT NOT NULL,
                price REAL,
                quantity REAL,
                state_before TEXT NOT NULL,
                state_after TEXT NOT NULL,
                order_id TEXT UNIQUE,
                status TEXT NOT NULL,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 포지션 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                state TEXT NOT NULL,
                entry_price REAL,
                entry_time DATETIME,
                exit_price REAL,
                exit_time DATETIME,
                quantity REAL,
                pnl REAL,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 주문 테이블 (중복 방지용)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT UNIQUE NOT NULL,
                symbol TEXT NOT NULL,
                order_type TEXT NOT NULL,
                side TEXT NOT NULL,
                price REAL,
                quantity REAL,
                status TEXT NOT NULL,
                executed_at DATETIME,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 인덱스 생성
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_timestamp ON signals(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_symbol ON signals(symbol)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_actions_timestamp ON actions(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_actions_order_id ON actions(order_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_order_id ON orders(order_id)")
        
        conn.commit()
        conn.close()
    
    def get_connection(self) -> sqlite3.Connection:
        """데이터베이스 연결 반환"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn
    
    def insert_signal(self, symbol: str, timeframe: str, signal_type: str, 
                     price: float, features: Optional[Dict] = None, 
                     metadata: Optional[Dict] = None) -> int:
        """
        시그널 기록
        
        Returns
        -------
        int
            삽입된 레코드 ID
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO signals (timestamp, symbol, timeframe, signal_type, price, features, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.utcnow(),
            symbol,
            timeframe,
            signal_type,
            price,
            json.dumps(features) if features else None,
            json.dumps(metadata) if metadata else None
        ))
        
        signal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return signal_id
    
    def insert_action(self, symbol: str, action_type: str, order_type: str,
                     price: Optional[float], quantity: Optional[float],
                     state_before: str, state_after: str,
                     order_id: Optional[str] = None, status: str = "PENDING",
                     metadata: Optional[Dict] = None) -> int:
        """
        액션 기록
        
        Returns
        -------
        int
            삽입된 레코드 ID
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO actions (timestamp, symbol, action_type, order_type, price, quantity,
                               state_before, state_after, order_id, status, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.utcnow(),
            symbol,
            action_type,
            order_type,
            price,
            quantity,
            state_before,
            state_after,
            order_id,
            status,
            json.dumps(metadata) if metadata else None
        ))
        
        action_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return action_id
    
    def insert_or_update_position(self, symbol: str, state: str,
                                  entry_price: Optional[float] = None,
                                  entry_time: Optional[datetime] = None,
                                  exit_price: Optional[float] = None,
                                  exit_time: Optional[datetime] = None,
                                  quantity: Optional[float] = None,
                                  pnl: Optional[float] = None,
                                  metadata: Optional[Dict] = None) -> int:
        """
        포지션 생성 또는 업데이트
        
        Returns
        -------
        int
            레코드 ID
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 기존 포지션 확인 (FLAT가 아닌 상태의 활성 포지션)
        cursor.execute("""
            SELECT id FROM positions 
            WHERE symbol = ? AND state != 'FLAT'
            ORDER BY updated_at DESC LIMIT 1
        """, (symbol,))
        
        existing = cursor.fetchone()
        
        if existing:
            # 업데이트
            cursor.execute("""
                UPDATE positions 
                SET state = ?, entry_price = ?, entry_time = ?, exit_price = ?, 
                    exit_time = ?, quantity = ?, pnl = ?, metadata = ?, 
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (state, entry_price, entry_time, exit_price, exit_time, 
                  quantity, pnl, json.dumps(metadata) if metadata else None, existing['id']))
            position_id = existing['id']
        else:
            # 새로 생성
            cursor.execute("""
                INSERT INTO positions (symbol, state, entry_price, entry_time, exit_price, 
                                     exit_time, quantity, pnl, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (symbol, state, entry_price, entry_time, exit_price, exit_time,
                  quantity, pnl, json.dumps(metadata) if metadata else None))
            position_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return position_id
    
    def check_order_exists(self, order_id: str) -> bool:
        """
        주문 ID 중복 확인 (idempotency)
        
        Returns
        -------
        bool
            주문이 존재하면 True
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM orders WHERE order_id = ?", (order_id,))
        exists = cursor.fetchone() is not None
        
        conn.close()
        return exists
    
    def insert_order(self, order_id: str, symbol: str, order_type: str, side: str,
                    price: Optional[float] = None, quantity: Optional[float] = None,
                    status: str = "PENDING", executed_at: Optional[datetime] = None,
                    metadata: Optional[Dict] = None) -> int:
        """
        주문 기록 (중복 방지)
        
        Returns
        -------
        int
            삽입된 레코드 ID
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO orders (order_id, symbol, order_type, side, price, quantity, 
                                  status, executed_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (order_id, symbol, order_type, side, price, quantity, status,
                  executed_at, json.dumps(metadata) if metadata else None))
            
            order_db_id = cursor.lastrowid
            conn.commit()
            return order_db_id
        except sqlite3.IntegrityError:
            # 중복 주문 ID
            conn.rollback()
            raise ValueError(f"Order ID {order_id} already exists (idempotency violation)")
        finally:
            conn.close()

