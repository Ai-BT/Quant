"""
CLI 도구: 각 단계별 실행 가능한 명령어
"""
import argparse
import sys
import random
from pathlib import Path
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))


def cmd_backtest(args):
    """백테스트 실행"""
    from app.backtest.engine import BacktestEngine
    from app.decision.engine import DecisionEngine
    from app.strategies.sma_strategy import SMAStrategy
    from app.core.database import Database
    from app.data.candle import Timeframe, Candle
    from datetime import datetime, timedelta
    import random
    
    print("백테스트 모드")
    print(f"전략: {args.strategy}")
    print(f"심볼: {args.symbol}")
    print(f"타임프레임: {args.timeframe}")
    
    # DB 초기화
    db = Database(args.db_path) if args.db else None
    
    # 전략 선택
    if args.strategy == "sma":
        strategy = SMAStrategy(fast_period=args.fast_period, slow_period=args.slow_period)
    else:
        print(f"알 수 없는 전략: {args.strategy}")
        return
    
    # DecisionEngine 생성
    decision_engine = DecisionEngine(strategy, args.symbol, db)
    
    # 백테스트 엔진 생성
    backtest_engine = BacktestEngine(decision_engine, initial_cash=args.initial_cash)
    
    # Mock 캔들 데이터 생성 (실제로는 거래소 API에서 가져와야 함)
    print("캔들 데이터 생성 중...")
    candles_by_timeframe = generate_mock_candles(args.symbol, args.timeframe, days=args.days)
    
    # 백테스트 실행
    result = backtest_engine.run(candles_by_timeframe, commission=args.commission)
    
    # 결과 출력
    print("\n=== 백테스트 결과 ===")
    print(f"초기 자본금: {result['initial_cash']:,.0f}원")
    print(f"최종 가치: {result['final_value']:,.0f}원")
    print(f"총 수익: {result['total_return']:,.0f}원 ({result['total_return_pct']:.2f}%)")
    print(f"총 거래 횟수: {result['total_trades']}")
    print(f"승리 거래: {result['winning_trades']}")
    print(f"패배 거래: {result['losing_trades']}")
    print(f"승률: {result['win_rate']:.2f}%")


def generate_mock_candles(symbol: str, timeframe_str: str, days: int = 30):
    """Mock 캔들 데이터 생성 (테스트용)"""
    from app.data.candle import Timeframe, Candle
    from datetime import datetime, timedelta
    
    # 타임프레임 파싱
    timeframe_map = {
        '1m': Timeframe.MIN_1,
        '5m': Timeframe.MIN_5,
        '15m': Timeframe.MIN_15,
        '30m': Timeframe.MIN_30,
        '1h': Timeframe.HOUR_1,
        '4h': Timeframe.HOUR_4,
        '1d': Timeframe.DAY_1
    }
    
    timeframe = timeframe_map.get(timeframe_str, Timeframe.MIN_15)
    
    # 시간 간격 계산
    if timeframe == Timeframe.MIN_1:
        delta = timedelta(minutes=1)
    elif timeframe == Timeframe.MIN_5:
        delta = timedelta(minutes=5)
    elif timeframe == Timeframe.MIN_15:
        delta = timedelta(minutes=15)
    elif timeframe == Timeframe.MIN_30:
        delta = timedelta(minutes=30)
    elif timeframe == Timeframe.HOUR_1:
        delta = timedelta(hours=1)
    elif timeframe == Timeframe.HOUR_4:
        delta = timedelta(hours=4)
    else:
        delta = timedelta(days=1)
    
    # 캔들 생성
    start_time = datetime.utcnow() - timedelta(days=days)
    candles = []
    
    base_price = 100_000  # 기본 가격
    current_price = base_price
    
    if delta.total_seconds() > 0:
        num_candles = int((days * 24 * 60) // delta.total_seconds() * 60)
    else:
        num_candles = days
    num_candles = min(int(num_candles), 1000)  # 최대 1000개
    
    for i in range(num_candles):
        timestamp = start_time + delta * i
        
        # 랜덤 워크로 가격 변동
        change_pct = (random.random() - 0.5) * 0.02  # ±1%
        current_price *= (1 + change_pct)
        
        high = current_price * (1 + abs(random.random() - 0.5) * 0.01)
        low = current_price * (1 - abs(random.random() - 0.5) * 0.01)
        open_price = current_price * (1 + (random.random() - 0.5) * 0.005)
        close_price = current_price
        volume = random.random() * 1000
        
        candle = Candle(
            timestamp=timestamp,
            open=open_price,
            high=high,
            low=low,
            close=close_price,
            volume=volume
        )
        candles.append(candle)
    
    return {timeframe: candles}


def cmd_live(args):
    """라이브 트레이딩 실행 (Paper Trading)"""
    from app.decision.engine import DecisionEngine
    from app.execution.executor import OrderExecutor
    from app.strategies.sma_strategy import SMAStrategy
    from app.api.mock_api import MockExchangeAPI
    from app.core.database import Database
    from app.core.logger import setup_logger
    
    logger = setup_logger("live_trading")
    
    print("라이브 트레이딩 모드 (Paper Trading)")
    print(f"전략: {args.strategy}")
    print(f"심볼: {args.symbol}")
    
    # DB 초기화
    db = Database(args.db_path)
    
    # Mock API (Paper Trading)
    exchange_api = MockExchangeAPI(initial_balance=args.initial_balance)
    
    # 전략 선택
    if args.strategy == "sma":
        strategy = SMAStrategy()
    else:
        print(f"알 수 없는 전략: {args.strategy}")
        return
    
    # DecisionEngine 생성
    decision_engine = DecisionEngine(strategy, args.symbol, db)
    
    # OrderExecutor 생성
    executor = OrderExecutor(exchange_api, db, args.symbol)
    
    logger.info("라이브 트레이딩 시작 (실제 구현 필요)")
    print("라이브 트레이딩은 아직 구현 중입니다.")
    print("실제로는 실시간 캔들 데이터를 수신하여 DecisionEngine을 호출해야 합니다.")


def cmd_check_db(args):
    """DB 상태 확인"""
    from app.core.database import Database
    import json
    
    db = Database(args.db_path)
    conn = db.get_connection()
    cursor = conn.cursor()
    
    print("=== 데이터베이스 상태 ===")
    
    # 시그널 개수
    cursor.execute("SELECT COUNT(*) FROM signals")
    signal_count = cursor.fetchone()[0]
    print(f"시그널 수: {signal_count}")
    
    # 액션 개수
    cursor.execute("SELECT COUNT(*) FROM actions")
    action_count = cursor.fetchone()[0]
    print(f"액션 수: {action_count}")
    
    # 포지션 개수
    cursor.execute("SELECT COUNT(*) FROM positions")
    position_count = cursor.fetchone()[0]
    print(f"포지션 수: {position_count}")
    
    # 주문 개수
    cursor.execute("SELECT COUNT(*) FROM orders")
    order_count = cursor.fetchone()[0]
    print(f"주문 수: {order_count}")
    
    conn.close()


def main():
    parser = argparse.ArgumentParser(description="코인 자동매매 시스템 CLI")
    subparsers = parser.add_subparsers(dest='command', help='명령어')
    
    # 백테스트 명령어
    backtest_parser = subparsers.add_parser('backtest', help='백테스트 실행')
    backtest_parser.add_argument('--strategy', default='sma', help='전략 (sma)')
    backtest_parser.add_argument('--symbol', default='KRW-BTC', help='심볼')
    backtest_parser.add_argument('--timeframe', default='15m', help='타임프레임')
    backtest_parser.add_argument('--fast-period', type=int, default=5, help='빠른 SMA 기간')
    backtest_parser.add_argument('--slow-period', type=int, default=20, help='느린 SMA 기간')
    backtest_parser.add_argument('--initial-cash', type=float, default=1_000_000, help='초기 자본금')
    backtest_parser.add_argument('--commission', type=float, default=0.0005, help='수수료율')
    backtest_parser.add_argument('--days', type=int, default=30, help='백테스트 기간 (일)')
    backtest_parser.add_argument('--db-path', default='db/trading.db', help='DB 경로')
    backtest_parser.add_argument('--db', action='store_true', help='DB에 기록')
    backtest_parser.set_defaults(func=cmd_backtest)
    
    # 라이브 트레이딩 명령어
    live_parser = subparsers.add_parser('live', help='라이브 트레이딩 실행')
    live_parser.add_argument('--strategy', default='sma', help='전략')
    live_parser.add_argument('--symbol', default='KRW-BTC', help='심볼')
    live_parser.add_argument('--initial-balance', type=float, default=1_000_000, help='초기 잔고')
    live_parser.add_argument('--db-path', default='db/trading.db', help='DB 경로')
    live_parser.set_defaults(func=cmd_live)
    
    # DB 확인 명령어
    db_parser = subparsers.add_parser('check-db', help='DB 상태 확인')
    db_parser.add_argument('--db-path', default='db/trading.db', help='DB 경로')
    db_parser.set_defaults(func=cmd_check_db)
    
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

