#!/bin/bash
# coin_auto_trading 검증 스크립트

echo "=========================================="
echo "coin_auto_trading 프로젝트 검증"
echo "=========================================="

# 프로젝트 디렉토리로 이동
cd /mnt/c/Users/surro/Documents/01_test/coin_auto_trading || exit 1

# 가상환경 활성화 (경로 확인 필요)
if [ -f "../quant_env/bin/activate" ]; then
    source ../quant_env/bin/activate
    echo "✅ 가상환경 활성화: ../quant_env"
elif [ -f "quant_env/bin/activate" ]; then
    source quant_env/bin/activate
    echo "✅ 가상환경 활성화: quant_env"
elif [ -f "quent_env/bin/activate" ]; then
    source quent_env/bin/activate
    echo "✅ 가상환경 활성화: quent_env"
else
    echo "⚠️  가상환경을 찾을 수 없습니다. 수동으로 활성화해주세요."
    echo "   source ../quant_env/bin/activate"
    echo "   또는"
    echo "   source quent_env/bin/activate"
fi

echo ""
echo "1. Python 버전 확인"
python --version

echo ""
echo "2. CLI 도구 확인"
python cli.py --help | head -20

echo ""
echo "3. 상태 머신 테스트"
python -c "
from app.core.state_machine import StateMachine, PositionState
sm = StateMachine()
print('✅ 상태 머신 import 성공')
print('   초기 상태:', sm.get_state().value)
sm.transition_to(PositionState.LONG, '매수 테스트')
print('   매수 후 상태:', sm.get_state().value)
"

echo ""
echo "4. 기술적 지표 테스트"
python -c "
from app.features.indicators import sma, ema, rsi
prices = [100, 102, 104, 103, 105, 107, 106, 108, 110, 109]
sma_result = sma(prices, 5)
print('✅ SMA 계산 성공')
print('   마지막 SMA 값:', sma_result[-1] if sma_result[-1] else 'None')
"

echo ""
echo "5. 백테스트 실행 (7일, Mock 데이터)"
python cli.py backtest \
  --strategy sma \
  --symbol KRW-BTC \
  --timeframe 15m \
  --days 7 \
  --fast-period 5 \
  --slow-period 20 \
  --initial-cash 1000000

echo ""
echo "=========================================="
echo "검증 완료!"
echo "=========================================="

