"""
MACD + Trend Filter 전략 구현

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
from app.core.logging import get_logger

logger = get_logger(__name__, "macd_strategy")


class MACDStrategy(BaseStrategy):
    """MACD + Trend Filter 전략"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        # MACD 설정
        self.macd_fast = self.config.get('macd_fast', 12)
        self.macd_slow = self.config.get('macd_slow', 26)
        self.macd_signal = self.config.get('macd_signal', 9)
        
        # Trend Filter 설정
        self.trend_ma_period = self.config.get('trend_ma_period', 200)
        self.trend_ma_type = self.config.get('trend_ma_type', 'SMA')
        self.use_trend_filter = self.config.get('use_trend_filter', True)
        self.use_dual_trend = self.config.get('use_dual_trend', False)
        self.mid_trend_period = self.config.get('mid_trend_period', 50)
        
        # 추가 필터
        self.use_histogram_filter = self.config.get('use_histogram_filter', True)
        self.min_histogram = self.config.get('min_histogram', 0)
        self.use_volume_filter = self.config.get('use_volume_filter', False)
        self.volume_ma_period = self.config.get('volume_ma_period', 20)
        self.volume_multiplier = self.config.get('volume_multiplier', 1.2)
        
        # 실시간 실행 설정
        self.check_interval = self.config.get('check_interval', 300)
        self.buy_amount_ratio = self.config.get('buy_amount_ratio', 0.1)
        self.sell_all_on_signal = self.config.get('sell_all_on_signal', True)
        self.candle_minutes = self.config.get('candle_minutes', 60)  # 1시간봉
        
        # 가격 히스토리 (MACD 계산용)
        self.price_history: List[Dict[str, Any]] = []
        self.max_history = max(self.trend_ma_period, self.macd_slow) * 2
        
        # 이전 포지션 상태
        self.last_position = 0
    
    async def initialize(self, account: VirtualAccount, upbit_adapter=None):
        """전략 초기화"""
        logger.info(f"MACD 전략 초기화: {self.name}")
        logger.info(f"설정: MACD({self.macd_fast}/{self.macd_slow}/{self.macd_signal}), Trend MA({self.trend_ma_period}), market={self.market}")
        self.price_history = []
        self.last_position = 0
        
        # 과거 데이터 로드 (이동평균 계산을 위해)
        if upbit_adapter:
            try:
                logger.info(f"과거 데이터 로드 시작: {self.market} ({self.candle_minutes}분봉)")
                # 1시간봉 데이터 가져오기 (최근 1000개)
                from strategies.core.data_fetcher import fetch_minute_data
                
                df = fetch_minute_data(
                    market=self.market,
                    minutes=self.candle_minutes,  # 1시간봉 (60분)
                    count=1000  # 최근 1000개 (약 41일 분량)
                )
                
                if not df.empty and len(df) > 0:
                    # price_history에 과거 데이터 채우기
                    for idx in range(len(df)):
                        row = df.iloc[idx]
                        self.price_history.append({
                            'price': row['종가'],
                            'volume': row.get('거래량', 0),
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
    
    def calculate_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """MACD, Signal, Histogram 계산"""
        df_copy = df.copy()
        
        # EMA 계산
        ema_fast = df_copy['종가'].ewm(span=self.macd_fast, adjust=False).mean()
        ema_slow = df_copy['종가'].ewm(span=self.macd_slow, adjust=False).mean()
        
        # MACD Line = Fast EMA - Slow EMA
        df_copy['MACD'] = ema_fast - ema_slow
        
        # Signal Line = MACD의 EMA
        df_copy['MACD_Signal'] = df_copy['MACD'].ewm(span=self.macd_signal, adjust=False).mean()
        
        # Histogram = MACD - Signal
        df_copy['MACD_Histogram'] = df_copy['MACD'] - df_copy['MACD_Signal']
        
        return df_copy
    
    def calculate_trend_ma(self, df: pd.DataFrame) -> pd.DataFrame:
        """Trend Filter용 이동평균 계산"""
        df_copy = df.copy()
        
        if self.trend_ma_type == 'SMA':
            df_copy['Trend_MA'] = df_copy['종가'].rolling(window=self.trend_ma_period).mean()
        else:  # EMA
            df_copy['Trend_MA'] = df_copy['종가'].ewm(span=self.trend_ma_period, adjust=False).mean()
        
        # 이중 트렌드 필터
        if self.use_dual_trend:
            if self.trend_ma_type == 'SMA':
                df_copy['Mid_Trend_MA'] = df_copy['종가'].rolling(window=self.mid_trend_period).mean()
            else:
                df_copy['Mid_Trend_MA'] = df_copy['종가'].ewm(span=self.mid_trend_period, adjust=False).mean()
        
        return df_copy
    
    async def execute(self, account: VirtualAccount, current_price: float, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """전략 실행"""
        currency = self.market.replace('KRW-', '')
        current_volume = market_data.get('volume', 0)
        current_timestamp = market_data.get('timestamp', pd.Timestamp.now())
        
        # 가격 히스토리 업데이트 (1시간봉 데이터이므로 1시간에 한 번만 추가)
        # 마지막 데이터의 시간과 현재 시간이 다른 시간대일 때만 추가
        should_add = True
        if len(self.price_history) > 0:
            last_data = self.price_history[-1]
            last_timestamp = pd.Timestamp(last_data['timestamp'])
            current_ts = pd.Timestamp(current_timestamp)
            
            # 같은 시간대면 추가하지 않음 (1시간봉 데이터이므로)
            # 시간 단위로 비교 (분과 초는 무시)
            last_hour = last_timestamp.replace(minute=0, second=0, microsecond=0)
            current_hour = current_ts.replace(minute=0, second=0, microsecond=0)
            
            if last_hour == current_hour:
                should_add = False
        
        if should_add:
            self.price_history.append({
                'price': current_price,
                'volume': current_volume,
                'timestamp': current_timestamp,
            })
        
        # 오래된 히스토리 제거
        if len(self.price_history) > self.max_history:
            self.price_history = self.price_history[-self.max_history:]
        
        # 이동평균 계산을 위한 데이터가 충분한지 확인
        min_required = max(self.trend_ma_period if self.use_trend_filter else 0, self.macd_slow)
        if len(self.price_history) < min_required:
            return {
                'signal': 'HOLD',
                'message': f'데이터 수집 중... ({len(self.price_history)}/{min_required})',
            }
        
        # DataFrame 생성
        df = pd.DataFrame(self.price_history)
        df['종가'] = df['price']
        if 'volume' in df.columns:
            df['거래량'] = df['volume']
        
        # MACD 계산
        df = self.calculate_macd(df)
        
        # Trend Filter 계산
        if self.use_trend_filter:
            df = self.calculate_trend_ma(df)
        
        # 현재 포지션 확인
        holdings = account.get_holdings()
        current_holdings = holdings.get(currency, 0)
        has_position = current_holdings > 0
        
        # MACD 크로스오버 감지
        macd_cross_up = (
            (df['MACD'].iloc[-1] > df['MACD_Signal'].iloc[-1]) &
            (df['MACD'].iloc[-2] <= df['MACD_Signal'].iloc[-2]) if len(df) >= 2 else False
        )
        
        macd_cross_down = (
            (df['MACD'].iloc[-1] < df['MACD_Signal'].iloc[-1]) &
            (df['MACD'].iloc[-2] >= df['MACD_Signal'].iloc[-2]) if len(df) >= 2 else False
        )
        
        # 매매 신호 판단
        signal = 'HOLD'
        message = ''
        
        if has_position:
            # 보유 중일 때: MACD 데드크로스 또는 추세 반전 시 매도
            sell_condition = macd_cross_down
            
            if self.use_trend_filter:
                trend_down = df['종가'].iloc[-1] < df['Trend_MA'].iloc[-1]
                sell_condition = sell_condition | trend_down
            
            if sell_condition:
                signal = 'SELL'
                message = f'MACD 데드크로스 또는 추세 반전, 전량 매도 (보유량: {current_holdings:.6f})'
        else:
            # 보유하지 않을 때: MACD 골든크로스 + 추세 조건 만족 시 매수
            buy_condition = macd_cross_up
            
            # Trend Filter 적용
            if self.use_trend_filter:
                trend_up = df['종가'].iloc[-1] > df['Trend_MA'].iloc[-1]
                buy_condition = buy_condition & trend_up
                
                # 이중 트렌드 필터
                if self.use_dual_trend:
                    mid_trend_up = df['종가'].iloc[-1] > df['Mid_Trend_MA'].iloc[-1]
                    ma_aligned = df['Mid_Trend_MA'].iloc[-1] > df['Trend_MA'].iloc[-1]
                    buy_condition = buy_condition & mid_trend_up & ma_aligned
            
            # Histogram 필터 적용
            if self.use_histogram_filter:
                histogram_positive = df['MACD_Histogram'].iloc[-1] > self.min_histogram
                buy_condition = buy_condition & histogram_positive
            
            if buy_condition:
                signal = 'BUY'
                balance = account.get_balance()
                buy_amount = balance * self.buy_amount_ratio
                message = f'MACD 골든크로스 + 추세 확인, 매수 (금액: {buy_amount:,.0f}원)'
        
        # 실제 거래 실행
        if signal == 'BUY' and not has_position:
            balance = account.get_balance()
            buy_amount = balance * self.buy_amount_ratio
            
            if buy_amount > 5000:  # 최소 주문 금액 체크
                success = account.buy(
                    currency=currency,
                    price=current_price,
                    amount=buy_amount,
                    commission=0.0005
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
            'macd': float(df['MACD'].iloc[-1]),
            'macd_signal': float(df['MACD_Signal'].iloc[-1]),
            'macd_histogram': float(df['MACD_Histogram'].iloc[-1]),
        }
    
    async def cleanup(self, account: VirtualAccount):
        """전략 종료 시 정리"""
        logger.info(f"MACD 전략 정리: {self.name}")

