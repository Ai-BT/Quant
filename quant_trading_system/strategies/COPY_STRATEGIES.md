# 전략 복사 가이드

`upbit_balance_checker` 폴더의 전략들을 `quant_trading_system/strategies`로 복사하는 방법입니다.

## 복사할 전략 목록

1. **sma_strategy** - SMA 골든크로스 전략
2. **macd_strategy** - MACD 전략
3. **momentum_strategy** - 모멘텀 전략
4. **goldcross_rsi_strategy** - 골든크로스 + RSI 전략

## 복사 방법

### Windows (PowerShell)

```powershell
# 프로젝트 루트에서 실행
cd quant_trading_system

# 각 전략 폴더 복사
Copy-Item -Path ..\upbit_balance_checker\strategies\sma_strategy -Destination strategies\sma_strategy -Recurse
Copy-Item -Path ..\upbit_balance_checker\strategies\macd_strategy -Destination strategies\macd_strategy -Recurse
Copy-Item -Path ..\upbit_balance_checker\strategies\momentum_strategy -Destination strategies\momentum_strategy -Recurse
Copy-Item -Path ..\upbit_balance_checker\strategies\goldcross_rsi_strategy -Destination strategies\goldcross_rsi_strategy -Recurse
```

### 또는 수동으로 복사

1. `upbit_balance_checker/strategies/` 폴더의 각 전략 폴더를
2. `quant_trading_system/strategies/` 폴더로 복사

## 복사 후 확인 사항

각 전략 폴더에는 다음 파일들이 있어야 합니다:
- `__init__.py`
- `config.py`
- `strategy.py`
- `run_*.py` (실행 파일들)
- `README.md` (있는 경우)

## Import 경로 수정

복사 후 각 전략 파일의 import 경로를 수정해야 할 수 있습니다:

```python
# 기존 (upbit_balance_checker 기준)
from core.indicators import calculate_sma

# 수정 후 (quant_trading_system 기준)
from strategies.core.indicators import calculate_sma
```

또는 상대 경로 사용:
```python
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from core.indicators import calculate_sma
```


