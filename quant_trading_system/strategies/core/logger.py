"""
로깅 유틸리티

백테스팅 결과를 화면과 파일에 동시에 기록
"""

import sys
from datetime import datetime
from pathlib import Path


class TeeLogger:
    """
    화면과 파일에 동시에 출력하는 로거
    """
    
    def __init__(self, log_file=None):
        """
        Parameters
        ----------
        log_file : str or Path, optional
            로그 파일 경로. None이면 화면에만 출력
        """
        self.terminal = sys.stdout
        self.log_file = None
        
        if log_file:
            self.log_file = open(log_file, 'w', encoding='utf-8')
    
    def write(self, message):
        """메시지를 화면과 파일에 동시에 쓰기"""
        self.terminal.write(message)
        if self.log_file:
            self.log_file.write(message)
    
    def flush(self):
        """버퍼 비우기"""
        self.terminal.flush()
        if self.log_file:
            self.log_file.flush()
    
    def close(self):
        """로그 파일 닫기"""
        if self.log_file:
            self.log_file.close()


def sanitize_filename(text: str) -> str:
    """
    파일명에서 한글 및 특수문자 제거
    
    Parameters
    ----------
    text : str
        원본 텍스트
    
    Returns
    -------
    str
        안전한 파일명
    """
    import re
    # 한글, 한자, 일본어 등 제거 (영문, 숫자, 일부 특수문자만 남김)
    safe_text = re.sub(r'[^\w\s-]', '', text, flags=re.ASCII)
    safe_text = re.sub(r'[-\s]+', '_', safe_text)
    return safe_text.strip('_')


def setup_logger(strategy_name: str, market: str, output_dir: str = "logs") -> TeeLogger:
    """
    로거 설정
    
    Parameters
    ----------
    strategy_name : str
        전략 이름
    market : str
        마켓 코드
    output_dir : str
        로그 저장 디렉토리
    
    Returns
    -------
    TeeLogger
        설정된 로거
    """
    # 로그 디렉토리 생성
    log_dir = Path(output_dir)
    log_dir.mkdir(exist_ok=True)
    
    # 파일명 생성 (타임스탬프 포함, 한글 제거)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_strategy = sanitize_filename(strategy_name)
    if not safe_strategy:  # 한글만 있어서 비어있으면 기본값 사용
        safe_strategy = "strategy"
    log_filename = f"{safe_strategy}_{market}_{timestamp}.log"
    log_path = log_dir / log_filename
    
    # TeeLogger 생성
    logger = TeeLogger(log_path)
    
    print(f"📝 로그 파일: {log_path}")
    print()
    
    return logger


def save_results_to_file(result: dict, config: dict, stats: dict, output_dir: str = "results"):
    """
    백테스팅 결과를 별도의 텍스트 파일로 저장
    
    Parameters
    ----------
    result : dict
        백테스팅 결과
    config : dict
        전략 설정
    stats : dict
        전략 통계
    output_dir : str
        결과 저장 디렉토리
    """
    # 결과 디렉토리 생성
    results_dir = Path(output_dir)
    results_dir.mkdir(exist_ok=True)
    
    # 파일명 생성 (한글 제거)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = sanitize_filename(config['name'])
    if not safe_name:
        safe_name = "strategy"
    result_filename = f"{safe_name}_{config['market']}_{timestamp}.txt"
    result_path = results_dir / result_filename
    
    # 결과 작성
    with open(result_path, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write(f"📊 백테스팅 결과 리포트\n")
        f.write("=" * 70 + "\n\n")
        
        # 기본 정보
        f.write(f"생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"전략: {config['name']}\n")
        f.write(f"마켓: {config['market']}\n\n")
        
        # 전략 설정
        f.write("=" * 70 + "\n")
        f.write("⚙️ 전략 설정\n")
        f.write("=" * 70 + "\n")
        for key, value in config.items():
            if key not in ['name']:
                f.write(f"{key}: {value}\n")
        f.write("\n")
        
        # 전략 통계
        if stats:
            f.write("=" * 70 + "\n")
            f.write("📊 전략 통계\n")
            f.write("=" * 70 + "\n")
            for key, value in stats.items():
                if key not in ['strategy_name']:
                    if isinstance(value, float):
                        f.write(f"{key}: {value:.4f}\n")
                    else:
                        f.write(f"{key}: {value}\n")
            f.write("\n")
        
        # 백테스팅 결과
        f.write("=" * 70 + "\n")
        f.write("💰 백테스팅 결과\n")
        f.write("=" * 70 + "\n")
        f.write(f"초기 자본: {result['initial_cash']:,.0f}원\n")
        f.write(f"최종 자산: {result['final_value']:,.0f}원\n")
        
        # 순이익 계산
        net_profit = result['final_value'] - result['initial_cash']
        f.write(f"순이익: {net_profit:,.0f}원\n")
        
        f.write(f"총 수익률: {result['total_return']:.2f}%\n")
        f.write(f"Buy & Hold: {result['buy_hold_return']:.2f}%\n")
        f.write(f"MDD: {result['mdd']:.2f}%\n")
        f.write(f"샤프 비율: {result['sharpe_ratio']:.2f}\n")
        f.write(f"거래 횟수: {result['num_trades']}회\n")
        f.write(f"승률: {result['win_rate']:.2f}%\n")
        f.write("\n")
        
        # 거래 내역 (전체)
        if result['num_trades'] > 0 and len(result['trades']) > 0:
            f.write("=" * 70 + "\n")
            f.write(f"📋 전체 거래 내역 (총 {len(result['trades'])}건)\n")
            f.write("=" * 70 + "\n\n")
            
            for i, trade in enumerate(result['trades'], 1):
                # dict 또는 객체 모두 처리
                if isinstance(trade, dict):
                    trade_type = trade['type']
                    trade_date = trade['date']
                    trade_price = trade['price']
                    trade_quantity = trade['quantity']
                    trade_portfolio = trade['portfolio_value']
                    trade_profit = trade.get('profit', None)
                    trade_profit_rate = trade.get('profit_rate', None)
                else:
                    trade_type = trade.type
                    trade_date = trade.date
                    trade_price = trade.price
                    trade_quantity = trade.quantity
                    trade_portfolio = trade.portfolio_value
                    trade_profit = None
                    trade_profit_rate = None
                
                # 날짜 포맷팅
                if hasattr(trade_date, 'strftime'):
                    date_str = trade_date.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    date_str = str(trade_date)
                
                # 거래 유형
                type_emoji = "🟢" if trade_type == 'BUY' else "🔴"
                type_text = "매수" if trade_type == 'BUY' else "매도"
                
                f.write(f"[거래 #{i}] {type_emoji} {type_text}\n")
                f.write(f"  날짜: {date_str}\n")
                f.write(f"  가격: {trade_price:,.0f}원\n")
                f.write(f"  수량: {trade_quantity:.8f}\n")
                f.write(f"  포트폴리오 가치: {trade_portfolio:,.0f}원\n")
                
                # 매도 시 수익률 표시
                if trade_type == 'SELL' and trade_profit is not None:
                    f.write(f"  수익: {trade_profit:+,.0f}원\n")
                    f.write(f"  수익률: {trade_profit_rate:+.2f}%\n")
                
                f.write("\n")
    
    print(f"💾 결과 파일 저장: {result_path}")


def save_trades_to_csv(result: dict, config: dict, output_dir: str = "results"):
    """
    거래 내역을 CSV 파일로 저장
    
    Parameters
    ----------
    result : dict
        백테스팅 결과
    config : dict
        전략 설정
    output_dir : str
        결과 저장 디렉토리
    """
    import pandas as pd
    
    if result['num_trades'] == 0:
        return
    
    # 결과 디렉토리 생성
    results_dir = Path(output_dir)
    results_dir.mkdir(exist_ok=True)
    
    # 파일명 생성 (한글 제거)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = sanitize_filename(config['name'])
    if not safe_name:
        safe_name = "strategy"
    csv_filename = f"{safe_name}_{config['market']}_{timestamp}_trades.csv"
    csv_path = results_dir / csv_filename
    
    # 거래 내역을 DataFrame으로 변환
    trades_data = []
    for trade in result['trades']:
        trades_data.append({
            'date': trade.date.strftime('%Y-%m-%d'),
            'type': trade.type,
            'price': trade.price,
            'quantity': trade.quantity,
            'cash_before': trade.cash_before,
            'cash_after': trade.cash_after,
            'holdings_before': trade.holdings_before,
            'holdings_after': trade.holdings_after,
            'portfolio_value': trade.portfolio_value
        })
    
    df = pd.DataFrame(trades_data)
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    print(f"💾 거래내역 CSV 저장: {csv_path}")


