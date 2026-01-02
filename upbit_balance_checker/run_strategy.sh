#!/bin/bash
# 전략 실행 통합 스크립트 (Bash 버전)
# 
# 사용법:
#   chmod +x run_strategy.sh
#   ./run_strategy.sh [전략번호]
#
# 전략번호 없이 실행하면 메뉴가 표시됩니다.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 전략 목록
declare -A STRATEGIES
STRATEGIES[1]="strategies/sma_strategy/run_sma5_20.py:SMA 5/20 골든크로스 (일봉)"
STRATEGIES[2]="strategies/sma_strategy/run_sma20_50.py:SMA 20/50 골든크로스 (일봉)"
STRATEGIES[3]="strategies/sma_strategy/run_sma_minute.py:SMA 분봉 전략 (5캔들/30캔들)"
STRATEGIES[4]="strategies/macd_strategy/run_macd.py:MACD + Trend Filter"
STRATEGIES[5]="strategies/momentum_strategy/run_momentum.py:Momentum 전략"
STRATEGIES[6]="strategies/goldcross_rsi_strategy/run_backtest.py:Gold Cross + RSI 전략"

print_menu() {
    # Python 스크립트에서 동적으로 이름 가져오기
    local name1=$(cd "$SCRIPT_DIR" && python3 -c "import sys; sys.path.insert(0, '.'); from strategies.sma_strategy.config import SMA5_20_CONFIG; print(SMA5_20_CONFIG['name'])" 2>/dev/null || echo "SMA 5/20 골든크로스")
    local name2=$(cd "$SCRIPT_DIR" && python3 -c "import sys; sys.path.insert(0, '.'); from strategies.sma_strategy.config import SMA20_50_CONFIG; print(SMA20_50_CONFIG['name'])" 2>/dev/null || echo "SMA 20/50 골든크로스")
    local name3=$(cd "$SCRIPT_DIR" && python3 -c "import sys; sys.path.insert(0, '.'); from strategies.sma_strategy.config import SMA_MINUTE_CONFIG; print(SMA_MINUTE_CONFIG['name'])" 2>/dev/null || echo "SMA 분봉 전략")
    
    echo "======================================================================"
    echo "🚀 백테스트 전략 실행"
    echo "======================================================================"
    echo ""
    echo "  [1] $name1"
    echo "  [2] $name2"
    echo "  [3] $name3"
    echo "  [4] MACD + Trend Filter"
    echo "  [5] Momentum 전략"
    echo "  [6] Gold Cross + RSI 전략"
    echo ""
    echo "  [0] 종료"
    echo "======================================================================"
    echo ""
}

get_strategy_name() {
    local strategy_path=$1
    local strategy_num=$2
    # Python 스크립트에서 동적으로 이름 가져오기
    if [[ "$strategy_path" == *"sma_strategy/run_sma5_20"* ]]; then
        cd "$SCRIPT_DIR" && python3 -c "import sys; sys.path.insert(0, '.'); from strategies.sma_strategy.config import SMA5_20_CONFIG; print(SMA5_20_CONFIG['name'])" 2>/dev/null || echo "SMA 5/20 골든크로스"
    elif [[ "$strategy_path" == *"sma_strategy/run_sma20_50"* ]]; then
        cd "$SCRIPT_DIR" && python3 -c "import sys; sys.path.insert(0, '.'); from strategies.sma_strategy.config import SMA20_50_CONFIG; print(SMA20_50_CONFIG['name'])" 2>/dev/null || echo "SMA 20/50 골든크로스"
    elif [[ "$strategy_path" == *"sma_strategy/run_sma_minute"* ]]; then
        cd "$SCRIPT_DIR" && python3 -c "import sys; sys.path.insert(0, '.'); from strategies.sma_strategy.config import SMA_MINUTE_CONFIG; print(SMA_MINUTE_CONFIG['name'])" 2>/dev/null || echo "SMA 분봉 전략"
    else
        # 기본값 사용
        local strategy_info="${STRATEGIES[$strategy_num]}"
        echo "${strategy_info##*:}"
    fi
}

run_strategy() {
    local strategy_num=$1
    local strategy_info="${STRATEGIES[$strategy_num]}"
    
    if [ -z "$strategy_info" ]; then
        echo "❌ 잘못된 전략 번호입니다: $strategy_num"
        return 1
    fi
    
    local strategy_path="${strategy_info%%:*}"
    local strategy_name=$(get_strategy_name "$strategy_path" "$strategy_num")
    local full_path="$SCRIPT_DIR/$strategy_path"
    
    if [ ! -f "$full_path" ]; then
        echo "❌ 오류: 파일을 찾을 수 없습니다: $full_path"
        return 1
    fi
    
    echo ""
    echo "======================================================================"
    echo "▶️  $strategy_name 실행 중..."
    echo "======================================================================"
    echo ""
    echo "📂 실행 파일: $strategy_path"
    echo ""
    
    cd "$SCRIPT_DIR" || exit 1
    python3 "$strategy_path"
    
    return $?
}

main() {
    if [ $# -eq 0 ]; then
        # 메뉴 모드
        while true; do
            print_menu
            read -p "실행할 전략을 선택하세요: " choice
            
            if [ "$choice" = "0" ]; then
                echo ""
                echo "👋 종료합니다."
                exit 0
            fi
            
            if [ -z "${STRATEGIES[$choice]}" ]; then
                echo ""
                echo "❌ 잘못된 선택입니다: $choice"
                echo "다시 선택해주세요."
                echo ""
                continue
            fi
            
            run_strategy "$choice"
            
            echo ""
            echo "======================================================================"
            if [ $? -eq 0 ]; then
                echo "✅ 전략 실행 완료!"
            else
                echo "❌ 전략 실행 실패"
            fi
            echo "======================================================================"
            echo ""
            read -p "계속하려면 Enter를 누르세요..."
            echo ""
            echo ""
        done
    else
        # 직접 실행 모드
        run_strategy "$1"
    fi
}

main "$@"

