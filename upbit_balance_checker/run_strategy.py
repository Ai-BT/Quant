#!/usr/bin/env python3
"""
전략 실행 통합 스크립트

upbit_balance_checker 디렉토리에서 실행:
    python run_strategy.py
"""

import sys
import subprocess
from pathlib import Path

# 현재 스크립트의 디렉토리 (upbit_balance_checker)
SCRIPT_DIR = Path(__file__).parent.resolve()

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(SCRIPT_DIR))

# 전략 목록 (동적으로 이름 가져오기)
def _get_strategy_name(path: str) -> str:
    """전략 파일에서 실제 이름 가져오기"""
    try:
        if 'sma_strategy/run_sma5_20' in path:
            from strategies.sma_strategy.config import SMA5_20_CONFIG
            return SMA5_20_CONFIG['name']
        elif 'sma_strategy/run_sma20_50' in path:
            from strategies.sma_strategy.config import SMA20_50_CONFIG
            return SMA20_50_CONFIG['name']
        elif 'sma_strategy/run_sma_minute' in path:
            from strategies.sma_strategy.config import SMA_MINUTE_CONFIG
            return SMA_MINUTE_CONFIG['name']
        elif 'macd_strategy' in path:
            return 'MACD + Trend Filter'
        elif 'momentum_strategy' in path:
            return 'Momentum 전략'
        elif 'goldcross_rsi_strategy' in path:
            return 'Gold Cross + RSI 전략'
    except:
        pass
    return '알 수 없는 전략'

STRATEGIES = {
    '1': {
        'name': None,  # 동적으로 가져옴
        'path': 'strategies/sma_strategy/run_sma5_20.py',
        'description': '단기 이동평균선(5)과 중기 이동평균선(20) 크로스 전략'
    },
    '2': {
        'name': None,  # 동적으로 가져옴
        'path': 'strategies/sma_strategy/run_sma20_50.py',
        'description': '중기 이동평균선(20)과 장기 이동평균선(50) 크로스 전략'
    },
    '3': {
        'name': None,  # 동적으로 가져옴
        'path': 'strategies/sma_strategy/run_sma_minute.py',
        'description': '분봉 기반 초단기 트레이딩 전략'
    },
    '4': {
        'name': 'MACD + Trend Filter',
        'path': 'strategies/macd_strategy/run_macd.py',
        'description': 'MACD 지표와 추세 필터를 결합한 전략'
    },
    '5': {
        'name': 'Momentum 전략',
        'path': 'strategies/momentum_strategy/run_momentum.py',
        'description': '모멘텀 지표 기반 전략'
    },
    '6': {
        'name': 'Gold Cross + RSI 전략',
        'path': 'strategies/goldcross_rsi_strategy/run_backtest.py',
        'description': '골든크로스와 RSI를 결합한 전략'
    },
}

# 동적으로 이름 가져오기
for key, strategy in STRATEGIES.items():
    if strategy['name'] is None:
        strategy['name'] = _get_strategy_name(strategy['path'])


def print_menu():
    """메뉴 출력"""
    print("=" * 70)
    print("🚀 백테스트 전략 실행")
    print("=" * 70)
    print()
    
    for key, strategy in STRATEGIES.items():
        print(f"  [{key}] {strategy['name']}")
        print(f"      └─ {strategy['description']}")
        print()
    
    print("  [0] 종료")
    print("=" * 70)
    print()


def run_strategy(strategy_path: str):
    """전략 실행"""
    script_path = SCRIPT_DIR / strategy_path
    
    if not script_path.exists():
        print(f"❌ 오류: 파일을 찾을 수 없습니다: {script_path}")
        return False
    
    print(f"📂 실행 파일: {strategy_path}")
    print("=" * 70)
    print()
    
    try:
        # Python 스크립트 실행
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(SCRIPT_DIR),
            check=False
        )
        
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단되었습니다.")
        return False
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        return False


def main():
    """메인 함수"""
    while True:
        print_menu()
        
        try:
            choice = input("실행할 전략을 선택하세요: ").strip()
            
            if choice == '0':
                print("\n👋 종료합니다.")
                break
            
            if choice not in STRATEGIES:
                print(f"\n❌ 잘못된 선택입니다: {choice}")
                print("다시 선택해주세요.\n")
                continue
            
            strategy = STRATEGIES[choice]
            
            print()
            print("=" * 70)
            print(f"▶️  {strategy['name']} 실행 중...")
            print("=" * 70)
            print()
            
            success = run_strategy(strategy['path'])
            
            if success:
                print()
                print("=" * 70)
                print("✅ 전략 실행 완료!")
                print("=" * 70)
            else:
                print()
                print("=" * 70)
                print("❌ 전략 실행 실패")
                print("=" * 70)
            
            print()
            input("계속하려면 Enter를 누르세요...")
            print("\n" * 2)
            
        except KeyboardInterrupt:
            print("\n\n👋 종료합니다.")
            break
        except EOFError:
            print("\n\n👋 종료합니다.")
            break


if __name__ == "__main__":
    main()

