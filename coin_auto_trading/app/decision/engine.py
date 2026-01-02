"""
Decision Engine: 백테스트와 라이브에서 공통 사용하는 결정 엔진
"""
from typing import Dict, Optional, List
from app.data.candle import Candle, Timeframe
from app.core.state_machine import StateMachine, PositionState
from app.strategies.base_strategy import BaseStrategy
from app.features.indicators import calculate_features
from app.core.database import Database
from app.core.logger import setup_logger

logger = setup_logger(__name__)


class DecisionEngine:
    """결정 엔진 (백테스트와 라이브 공통)"""
    
    def __init__(self, strategy: BaseStrategy, symbol: str, db: Optional[Database] = None):
        """
        초기화
        
        Parameters
        ----------
        strategy : BaseStrategy
            사용할 전략
        symbol : str
            거래 심볼 (예: "KRW-BTC")
        db : Database, optional
            데이터베이스 (없으면 기록 안 함)
        """
        self.strategy = strategy
        self.symbol = symbol
        self.db = db
        self.state_machine = StateMachine()
        logger.info(f"DecisionEngine initialized: symbol={symbol}, strategy={strategy.name}")
    
    def decide(self, candles: Dict[Timeframe, List[Candle]], 
              current_price: float) -> Dict:
        """
        결정 수행 (캔들 마감 이벤트에서 호출)
        
        Parameters
        ----------
        candles : Dict[Timeframe, List[Candle]]
            타임프레임별 캔들 데이터
        current_price : float
            현재 가격
        
        Returns
        -------
        dict
            {
                'action': 'BUY' | 'SELL' | 'HOLD',
                'confidence': float,
                'reason': str,
                'state_before': str,
                'state_after': str,
                'metadata': dict
            }
        """
        current_state = self.state_machine.get_state()
        
        # 필요한 타임프레임 확인
        required_timeframes = self.strategy.get_required_timeframes()
        for tf in required_timeframes:
            if tf not in candles or not candles[tf]:
                logger.warning(f"Missing required timeframe: {tf}")
                return {
                    'action': 'HOLD',
                    'confidence': 0.0,
                    'reason': f'Missing required timeframe: {tf}',
                    'state_before': current_state.value,
                    'state_after': current_state.value,
                    'metadata': {}
                }
        
        # 피처 계산
        # 기본 타임프레임에서 피처 계산 (첫 번째 타임프레임 사용)
        primary_timeframe = required_timeframes[0]
        primary_candles = candles[primary_timeframe]
        features = calculate_features(primary_candles)
        
        # 전략으로부터 시그널 생성
        signal = self.strategy.generate_signal(candles, current_state, features)
        
        action = signal.get('action', 'HOLD')
        confidence = signal.get('confidence', 0.0)
        reason = signal.get('reason', '')
        metadata = signal.get('metadata', {})
        
        # 상태 전환 결정
        new_state = current_state
        if action == 'BUY' and current_state == PositionState.FLAT:
            new_state = PositionState.LONG
        elif action == 'SELL' and current_state == PositionState.LONG:
            new_state = PositionState.FLAT
        # PENDING 상태는 execution 모듈에서 처리
        
        # DB에 시그널 기록
        if self.db:
            try:
                self.db.insert_signal(
                    symbol=self.symbol,
                    timeframe=primary_timeframe.value,
                    signal_type=action,
                    price=current_price,
                    features=features,
                    metadata=metadata
                )
            except Exception as e:
                logger.error(f"Failed to insert signal to DB: {e}")
        
        result = {
            'action': action,
            'confidence': confidence,
            'reason': reason,
            'state_before': current_state.value,
            'state_after': new_state.value,
            'metadata': {
                **metadata,
                'current_price': current_price,
                'features': {k: (v[-1] if isinstance(v, list) and v else v) 
                            for k, v in features.items() if not isinstance(v, dict)}
            }
        }
        
        logger.info(f"Decision made: {action} (confidence={confidence:.2f}, "
                   f"state={current_state.value}->{new_state.value})")
        
        return result
    
    def apply_decision(self, decision: Dict):
        """
        결정 적용 (상태 머신 업데이트)
        
        Parameters
        ----------
        decision : dict
            decide() 메서드의 결과
        """
        state_before = PositionState(decision['state_before'])
        state_after = PositionState(decision['state_after'])
        
        if state_before != state_after:
            self.state_machine.transition_to(
                state_after,
                reason=decision.get('reason', ''),
                metadata=decision.get('metadata', {})
            )
            
            logger.info(f"State transition: {state_before.value} -> {state_after.value}")
    
    def get_state(self) -> PositionState:
        """현재 상태 반환"""
        return self.state_machine.get_state()

