"""
SOL 코인 SMA 골든크로스 전략 구현

실시간 실행 가능한 전략
"""

import pandas as pd
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

# 프로젝트 루트 경로 추가
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.base_strategy import BaseStrategy
from app.core.virtual_account import VirtualAccount
from strategies.core.indicators import calculate_sma, detect_golden_cross, detect_dead_cross
from app.core.logging import get_logger

logger = get_logger(__name__, "sol_sma_strategy")


class SOLSMAStrategy(BaseStrategy):
    """SOL 코인 SMA 골든크로스 전략"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.fast_period = self.config.get('fast_period', 5)
        self.slow_period = self.config.get('slow_period', 20)
        self.check_interval = self.config.get('check_interval', 300)
        self.buy_amount_ratio = self.config.get('buy_amount_ratio', 0.1)
        self.sell_all_on_signal = self.config.get('sell_all_on_signal', True)
        
        # 가격 히스토리 (이동평균 계산용)
        self.price_history: List[Dict[str, Any]] = []
        self.max_history = max(self.fast_period, self.slow_period) * 2  # 충분한 히스토리
        
        # 이전 포지션 상태
        self.last_position = 0  # 1: 매수, 0: 현금
        
    async def initialize(self, account: VirtualAccount, upbit_adapter=None):
        """
        전략 초기화
        
        Parameters
        ----------
        account : VirtualAccount
            가상 계좌
        upbit_adapter : UpbitAdapter, optional
            Upbit API 어댑터 (과거 데이터 로드용)
        """
        logger.info(f"SOL SMA 전략 초기화: {self.name}")
        logger.info(f"설정: fast={self.fast_period}, slow={self.slow_period}, market={self.market}")
        self.price_history = []
        self.last_position = 0
        
        # 과거 데이터 로드 (이동평균 계산을 위해)
        if upbit_adapter:
            try:
                logger.info(f"과거 데이터 로드 시작: {self.market}")
                # 분봉 데이터 가져오기 (최근 200개, 5분봉)
                from strategies.core.data_fetcher import fetch_minute_data
                
                df = fetch_minute_data(
                    market=self.market,
                    minutes=5,  # 5분봉
                    count=200  # 최근 200개 (약 16시간 분량)
                )
                
                if not df.empty and len(df) > 0:
                    # price_history에 과거 데이터 채우기 (날짜순으로 정렬되어 있음)
                    for idx in range(len(df)):
                        row = df.iloc[idx]
                        self.price_history.append({
                            'price': row['종가'],
                            'timestamp': row.name if hasattr(row.name, 'isoformat') else pd.Timestamp.now(),
                        })
                    
                    logger.info(f"과거 데이터 로드 완료: {len(self.price_history)}개 데이터 포인트")
                    logger.info(f"첫 번째 데이터: {self.price_history[0]['price']:,.0f}원, 마지막 데이터: {self.price_history[-1]['price']:,.0f}원")
                else:
                    logger.warning("과거 데이터를 가져올 수 없습니다. 실시간 데이터 수집부터 시작합니다.")
            except Exception as e:
                logger.warning(f"과거 데이터 로드 실패: {e}. 실시간 데이터 수집부터 시작합니다.", exc_info=True)
        else:
            logger.info("UpbitAdapter가 없어 실시간 데이터 수집부터 시작합니다.")
    
    async def execute(self, account: VirtualAccount, current_price: float, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        전략 실행
        
        Parameters
        ----------
        account : VirtualAccount
            가상 계좌
        current_price : float
            현재가
        market_data : Dict[str, Any]
            시장 데이터
        
        Returns
        -------
        Dict[str, Any]
            실행 결과
        """
        # 가격 히스토리 업데이트 (중복 방지: 마지막 데이터와 같은 가격이면 추가하지 않음)
        currency = self.market.replace('KRW-', '')  # 'SOL'
        
        # 현재 시각
        current_timestamp = market_data.get('timestamp', pd.Timestamp.now())
        
        # 마지막 데이터와 시간 차이 확인 (같은 데이터 중복 방지)
        should_add = True
        if len(self.price_history) > 0:
            last_data = self.price_history[-1]
            # 마지막 데이터와 가격이 같으면 추가하지 않음 (같은 시점 데이터 중복 방지)
            if abs(last_data['price'] - current_price) < 0.01:
                should_add = False
        
        if should_add:
            self.price_history.append({
                'price': current_price,
                'timestamp': current_timestamp,
            })
        
        # 오래된 히스토리 제거
        if len(self.price_history) > self.max_history:
            self.price_history = self.price_history[-self.max_history:]
        
        # 이동평균 계산을 위한 데이터가 충분한지 확인
        if len(self.price_history) < self.slow_period:
            return {
                'signal': 'HOLD',
                'message': f'데이터 수집 중... ({len(self.price_history)}/{self.slow_period})',
            }
        
        # DataFrame 생성
        df = pd.DataFrame(self.price_history)
        df['종가'] = df['price']
        
        # 이동평균 계산
        df['SMA_fast'] = calculate_sma(df, column='종가', window=self.fast_period)
        df['SMA_slow'] = calculate_sma(df, column='종가', window=self.slow_period)
        
        # 골든크로스/데드크로스 탐지
        golden_cross = detect_golden_cross(df, self.fast_period, self.slow_period)
        dead_cross = detect_dead_cross(df, self.fast_period, self.slow_period)
        
        # 현재 포지션 확인
        holdings = account.get_holdings()
        current_holdings = holdings.get(currency, 0)
        has_position = current_holdings > 0
        
        # 매매 신호 판단
        signal = 'HOLD'
        message = ''
        
        if has_position:
            # 보유 중일 때: 데드크로스면 매도
            if dead_cross.iloc[-1]:
                signal = 'SELL'
                message = f'데드크로스 발생, 전량 매도 (보유량: {current_holdings:.6f})'
            elif df['SMA_fast'].iloc[-1] < df['SMA_slow'].iloc[-1]:
                # 단기선이 장기선 아래로 내려갔지만 크로스는 아닌 경우
                signal = 'SELL'
                message = f'단기선 < 장기선, 전량 매도 (보유량: {current_holdings:.6f})'
        else:
            # 보유하지 않을 때: 골든크로스면 매수
            if golden_cross.iloc[-1]:
                signal = 'BUY'
                balance = account.get_balance()
                buy_amount = balance * self.buy_amount_ratio
                message = f'골든크로스 발생, 매수 (금액: {buy_amount:,.0f}원)'
            elif df['SMA_fast'].iloc[-1] > df['SMA_slow'].iloc[-1]:
                # 단기선이 장기선 위에 있지만 크로스는 아닌 경우
                signal = 'BUY'
                balance = account.get_balance()
                buy_amount = balance * self.buy_amount_ratio
                message = f'단기선 > 장기선, 매수 (금액: {buy_amount:,.0f}원)'
        
        # 실제 거래 실행
        if signal == 'BUY' and not has_position:
            balance = account.get_balance()
            buy_amount = balance * self.buy_amount_ratio
            
            if buy_amount > 5000:  # 최소 주문 금액 체크
                success = account.buy(
                    currency=currency,
                    price=current_price,
                    amount=buy_amount,
                    commission=0.0005  # 0.05%
                )
                
                if success:
                    logger.info(f"매수 실행: {currency} @ {current_price:,.0f}원, 금액: {buy_amount:,.0f}원")
                    self.last_position = 1
                else:
                    logger.warning(f"매수 실패: 잔고 부족 또는 기타 오류")
                    signal = 'HOLD'
                    message = '매수 실행 실패 (잔고 부족)'
        
        elif signal == 'SELL' and has_position:
            success = account.sell(
                currency=currency,
                price=current_price,
                quantity=current_holdings,
                commission=0.0005
            )
            
            if success:
                logger.info(f"매도 실행: {currency} {current_holdings:.6f}개 @ {current_price:,.0f}원")
                self.last_position = 0
            else:
                logger.warning(f"매도 실패")
                signal = 'HOLD'
                message = '매도 실행 실패'
        
        return {
            'signal': signal,
            'message': message,
            'current_price': current_price,
            'sma_fast': float(df['SMA_fast'].iloc[-1]),
            'sma_slow': float(df['SMA_slow'].iloc[-1]),
        }
    
    async def cleanup(self, account: VirtualAccount):
        """전략 종료 시 정리"""
        logger.info(f"SOL SMA 전략 정리: {self.name}")
        # 필요 시 포지션 청산 등 정리 작업 수행

