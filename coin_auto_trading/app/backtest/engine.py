"""
백테스트 엔진: DecisionEngine을 사용한 백테스트
"""
from typing import List, Dict, Optional
from app.data.candle import Candle, Timeframe
from app.decision.engine import DecisionEngine
from app.core.state_machine import PositionState
from app.core.database import Database
from app.core.logger import setup_logger

logger = setup_logger(__name__)


class BacktestEngine:
    """백테스트 엔진"""
    
    def __init__(self, decision_engine: DecisionEngine, initial_cash: float = 1_000_000):
        """
        초기화
        
        Parameters
        ----------
        decision_engine : DecisionEngine
            결정 엔진 (백테스트와 라이브 공통)
        initial_cash : float
            초기 자본금
        """
        self.decision_engine = decision_engine
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions: List[Dict] = []
        self.trades: List[Dict] = []
        logger.info(f"BacktestEngine initialized with initial_cash={initial_cash}")
    
    def run(self, candles_by_timeframe: Dict[Timeframe, List[Candle]], 
           commission: float = 0.0005) -> Dict:
        """
        백테스트 실행
        
        Parameters
        ----------
        candles_by_timeframe : Dict[Timeframe, List[Candle]]
            타임프레임별 캔들 데이터
        commission : float
            수수료율 (0.0005 = 0.05%)
        
        Returns
        -------
        dict
            백테스트 결과
        """
        logger.info("Starting backtest...")
        
        # 모든 타임프레임에서 타임스탬프 추출 및 정렬
        all_timestamps = set()
        for candles in candles_by_timeframe.values():
            for candle in candles:
                all_timestamps.add(candle.timestamp)
        
        sorted_timestamps = sorted(all_timestamps)
        
        current_position: Optional[Dict] = None
        
        for timestamp in sorted_timestamps:
            # 해당 타임스탬프의 캔들 수집
            current_candles: Dict[Timeframe, List[Candle]] = {}
            
            for timeframe, candles in candles_by_timeframe.items():
                # 해당 시점까지의 캔들만 필터링
                candles_up_to_timestamp = [c for c in candles if c.timestamp <= timestamp]
                if candles_up_to_timestamp:
                    current_candles[timeframe] = candles_up_to_timestamp
            
            if not current_candles:
                continue
            
            # 현재 가격 (기본 타임프레임의 최신 캔들)
            primary_timeframe = list(current_candles.keys())[0]
            latest_candle = current_candles[primary_timeframe][-1]
            current_price = latest_candle.close
            
            # 캔들 마감 이벤트 확인 (간단화: 모든 타임스탬프에서 결정)
            # 실제로는 타임프레임별 마감 시간에만 결정해야 함
            
            # 결정 수행
            decision = self.decision_engine.decide(current_candles, current_price)
            
            action = decision.get('action')
            state_after = PositionState(decision['state_after'])
            
            # 거래 실행 (백테스트 시뮬레이션)
            if action == 'BUY' and self.decision_engine.get_state() == PositionState.FLAT:
                # 매수
                available_cash = self.cash
                cost = available_cash * (1 - commission)  # 수수료 제외
                quantity = cost / current_price
                
                if quantity > 0:
                    self.cash = 0
                    current_position = {
                        'entry_price': current_price,
                        'entry_time': timestamp,
                        'quantity': quantity
                    }
                    
                    trade = {
                        'timestamp': timestamp,
                        'action': 'BUY',
                        'price': current_price,
                        'quantity': quantity,
                        'value': cost
                    }
                    self.trades.append(trade)
                    
                    logger.debug(f"BUY at {timestamp}: {quantity:.6f} @ {current_price}")
            
            elif action == 'SELL' and current_position is not None:
                # 매도
                quantity = current_position['quantity']
                revenue = quantity * current_price * (1 - commission)
                
                self.cash += revenue
                
                pnl = revenue - (current_position['entry_price'] * quantity)
                pnl_pct = (pnl / (current_position['entry_price'] * quantity)) * 100
                
                trade = {
                    'timestamp': timestamp,
                    'action': 'SELL',
                    'price': current_price,
                    'quantity': quantity,
                    'value': revenue,
                    'entry_price': current_position['entry_price'],
                    'pnl': pnl,
                    'pnl_pct': pnl_pct
                }
                self.trades.append(trade)
                
                self.positions.append({
                    **current_position,
                    'exit_price': current_price,
                    'exit_time': timestamp,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct
                })
                
                logger.debug(f"SELL at {timestamp}: {quantity:.6f} @ {current_price} "
                           f"(PNL: {pnl:.2f}, {pnl_pct:.2f}%)")
                
                current_position = None
            
            # 상태 적용
            self.decision_engine.apply_decision(decision)
        
        # 최종 평가
        final_value = self.cash
        if current_position:
            # 미청산 포지션이 있으면 현재가로 평가
            latest_price = sorted_timestamps[-1]
            for tf, candles in candles_by_timeframe.items():
                for candle in reversed(candles):
                    if candle.timestamp == latest_price:
                        final_value += current_position['quantity'] * candle.close
                        break
        
        total_return = final_value - self.initial_cash
        total_return_pct = (total_return / self.initial_cash) * 100
        
        win_trades = [p for p in self.positions if p.get('pnl', 0) > 0]
        loss_trades = [p for p in self.positions if p.get('pnl', 0) < 0]
        
        result = {
            'initial_cash': self.initial_cash,
            'final_value': final_value,
            'total_return': total_return,
            'total_return_pct': total_return_pct,
            'total_trades': len(self.trades),
            'winning_trades': len(win_trades),
            'losing_trades': len(loss_trades),
            'win_rate': len(win_trades) / len(self.positions) * 100 if self.positions else 0,
            'trades': self.trades,
            'positions': self.positions
        }
        
        logger.info(f"Backtest completed: return={total_return_pct:.2f}%, "
                   f"trades={len(self.trades)}, win_rate={result['win_rate']:.2f}%")
        
        return result

