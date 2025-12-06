"""
실시간 가격 모니터링

5분 단위로 Upbit의 실시간 가격을 조회하고 출력하는 스크립트
"""

import requests
import time
from datetime import datetime
from typing import Dict, Optional


class PriceMonitor:
    """실시간 가격 모니터"""
    
    def __init__(self, market: str = 'KRW-BTC', interval: int = 300):
        """
        Parameters
        ----------
        market : str
            마켓 코드 (예: 'KRW-BTC', 'KRW-ETH')
        interval : int
            조회 간격 (초 단위, 기본 300초 = 5분)
        """
        self.market = market
        self.interval = interval
        self.base_url = "https://api.upbit.com/v1"
        self.headers = {"accept": "application/json"}
        self.running = False
    
    def get_current_price(self) -> Optional[Dict]:
        """
        현재가 조회
        
        Returns
        -------
        dict
            현재가 정보 (가격, 변동률 등)
        """
        url = f"{self.base_url}/ticker"
        params = {"markets": self.market}
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            if data:
                return data[0]
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ API 호출 오류: {e}")
            return None
    
    def format_price(self, price_data: Dict) -> str:
        """
        가격 정보 포맷팅
        
        Parameters
        ----------
        price_data : dict
            API 응답 데이터
        
        Returns
        -------
        str
            포맷팅된 문자열
        """
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        market = price_data.get('market', '')
        trade_price = price_data.get('trade_price', 0)
        signed_change_rate = price_data.get('signed_change_rate', 0) * 100
        signed_change_price = price_data.get('signed_change_price', 0)
        acc_trade_volume_24h = price_data.get('acc_trade_volume_24h', 0)
        high_price = price_data.get('high_price', 0)
        low_price = price_data.get('low_price', 0)
        
        # 변동률에 따른 색상 표시
        change_emoji = "📈" if signed_change_rate >= 0 else "📉"
        change_color = "상승" if signed_change_rate >= 0 else "하락"
        
        output = f"""
{'='*70}
⏰ {current_time}
{'='*70}
💰 마켓: {market}
💵 현재가: {trade_price:,.0f}원
{change_emoji} 변동률: {signed_change_rate:+.2f}% ({change_color})
💸 변동금액: {signed_change_price:+,.0f}원
📊 24시간 거래량: {acc_trade_volume_24h:,.2f}
📈 고가: {high_price:,.0f}원
📉 저가: {low_price:,.0f}원
{'='*70}
"""
        return output
    
    def monitor(self):
        """가격 모니터링 시작"""
        self.running = True
        print(f"🚀 실시간 가격 모니터링 시작")
        print(f"📊 마켓: {self.market}")
        print(f"⏱️  조회 간격: {self.interval}초 ({self.interval // 60}분)")
        print(f"⏹️  종료하려면 Ctrl+C를 누르세요\n")
        
        try:
            while self.running:
                price_data = self.get_current_price()
                
                if price_data:
                    output = self.format_price(price_data)
                    print(output)
                else:
                    print(f"❌ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 가격 조회 실패")
                
                # 다음 조회까지 대기
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  모니터링을 종료합니다.")
            self.running = False
        except Exception as e:
            print(f"\n❌ 오류 발생: {e}")
            self.running = False
    
    def stop(self):
        """모니터링 중지"""
        self.running = False


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Upbit 실시간 가격 모니터링')
    parser.add_argument(
        '--market',
        type=str,
        default='KRW-BTC',
        help='마켓 코드 (기본: KRW-BTC)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=300,
        help='조회 간격 (초 단위, 기본: 300초 = 5분)'
    )
    
    args = parser.parse_args()
    
    # 모니터 생성 및 실행
    monitor = PriceMonitor(market=args.market, interval=args.interval)
    monitor.monitor()


if __name__ == "__main__":
    main()

