"""
전략 로더

전략 폴더에서 전략을 동적으로 로드하는 모듈
"""

import importlib
import sys
from pathlib import Path
from typing import Dict, List, Optional, Type, Any
from app.core.logging import get_logger

logger = get_logger(__name__, "strategy_loader")

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
STRATEGIES_DIR = PROJECT_ROOT / "strategies"


class StrategyLoader:
    """전략 로더"""
    
    def __init__(self):
        self.strategies_dir = STRATEGIES_DIR
        self.loaded_strategies: Dict[str, Any] = {}
    
    def discover_strategies(self) -> List[str]:
        """
        전략 폴더에서 사용 가능한 전략 목록 조회
        
        Returns
        -------
        List[str]
            전략 이름 목록 (폴더명)
        """
        if not self.strategies_dir.exists():
            logger.warning(f"전략 폴더가 존재하지 않습니다: {self.strategies_dir}")
            return []
        
        strategies = []
        for item in self.strategies_dir.iterdir():
            if item.is_dir() and not item.name.startswith('_') and item.name != 'core':
                # __init__.py 또는 strategy.py가 있는지 확인
                if (item / "__init__.py").exists() or (item / "strategy.py").exists():
                    strategies.append(item.name)
        
        return sorted(strategies)
    
    def load_strategy(self, strategy_name: str):
        """
        전략 모듈 로드
        
        Parameters
        ----------
        strategy_name : str
            전략 이름 (폴더명)
        
        Returns
        -------
        Any
            전략 클래스 또는 모듈
        """
        if strategy_name in self.loaded_strategies:
            return self.loaded_strategies[strategy_name]
        
        strategy_path = self.strategies_dir / strategy_name
        if not strategy_path.exists():
            raise ValueError(f"전략을 찾을 수 없습니다: {strategy_name}")
        
        # strategy.py 파일이 있는지 확인
        strategy_file = strategy_path / "strategy.py"
        if not strategy_file.exists():
            raise ValueError(f"전략 파일을 찾을 수 없습니다: {strategy_file}")
        
        # 모듈 경로 생성
        module_path = f"strategies.{strategy_name}.strategy"
        
        try:
            # 전략 폴더를 sys.path에 추가
            if str(self.strategies_dir.parent) not in sys.path:
                sys.path.insert(0, str(self.strategies_dir.parent))
            
            # 이미 로드된 모듈이 있으면 제거
            if module_path in sys.modules:
                del sys.modules[module_path]
            
            # 모듈 로드
            module = importlib.import_module(module_path)
            
            # Strategy 클래스 찾기
            strategy_class = None
            
            # strategy 제거 후 파스칼케이스로 변환 (예: sol_sma_strategy -> SOLSMAStrategy)
            name_parts = strategy_name.replace('_strategy', '').split('_')
            if len(name_parts) > 0:
                # 각 단어를 대문자로 변환하여 연결
                camel_case = ''.join(word.upper() if len(word) <= 3 else word.capitalize() for word in name_parts) + 'Strategy'
                # sol_sma -> SOLSMAStrategy, macd -> MACDStrategy
                if hasattr(module, camel_case):
                    attr = getattr(module, camel_case)
                    if isinstance(attr, type):
                        strategy_class = attr
                        logger.info(f"전략 클래스 찾음 (이름 패턴): {camel_case}")
            
            # 위 방법으로 못 찾으면 Strategy로 끝나는 모든 클래스 확인
            if strategy_class is None:
                for attr_name in dir(module):
                    # BaseStrategy는 제외 (import된 클래스)
                    if attr_name in ('BaseStrategy', 'Strategy', '__class__', '__module__'):
                        continue
                    attr = getattr(module, attr_name)
                    # 타입이고 Strategy로 끝나며, 이 모듈에 정의된 클래스여야 함
                    if (isinstance(attr, type) and 
                        attr_name.endswith('Strategy')):
                        # 모듈 경로 확인 (import된 클래스 제외)
                        if hasattr(attr, '__module__'):
                            attr_module = attr.__module__
                            # 이 모듈에서 정의된 클래스이거나, 최소한 strategies 패키지 내의 클래스
                            if attr_module == module_path or attr_module.startswith('strategies.'):
                                strategy_class = attr
                                logger.info(f"전략 클래스 찾음: {attr_name} (모듈: {attr_module})")
                                break
            
            if strategy_class is None:
                available_classes = [name for name in dir(module) 
                                   if name.endswith('Strategy') and 
                                   isinstance(getattr(module, name, None), type)]
                raise ValueError(f"전략 클래스를 찾을 수 없습니다: {module_path} (사용 가능한 클래스: {available_classes})")
            
            self.loaded_strategies[strategy_name] = strategy_class
            logger.info(f"전략 로드 완료: {strategy_name}")
            return strategy_class
            
        except Exception as e:
            logger.error(f"전략 로드 실패: {strategy_name}, 오류: {e}", exc_info=True)
            raise
    
    def get_strategy_info(self, strategy_name: str) -> Dict[str, Any]:
        """
        전략 정보 조회
        
        Parameters
        ----------
        strategy_name : str
            전략 이름
        
        Returns
        -------
        Dict[str, Any]
            전략 정보
        """
        strategy_path = self.strategies_dir / strategy_name
        
        info = {
            'name': strategy_name,
            'path': str(strategy_path),
            'exists': strategy_path.exists(),
        }
        
        # config.py 파일 읽기
        config_file = strategy_path / "config.py"
        if config_file.exists():
            try:
                config_module = importlib.import_module(f"strategies.{strategy_name}.config")
                # 설정 정보 추출
                info['config'] = {
                    attr: getattr(config_module, attr) 
                    for attr in dir(config_module) 
                    if not attr.startswith('_') and isinstance(getattr(config_module, attr), (str, int, float, dict, list))
                }
            except Exception as e:
                logger.warning(f"설정 파일 읽기 실패: {config_file}, 오류: {e}")
        
        # README.md 파일 읽기
        readme_file = strategy_path / "README.md"
        if readme_file.exists():
            info['readme'] = readme_file.read_text(encoding='utf-8')
        
        return info


# 전역 전략 로더 인스턴스
strategy_loader = StrategyLoader()

