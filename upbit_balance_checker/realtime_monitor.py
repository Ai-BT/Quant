"""
실시간 가격 모니터링 사용 예시

간단하게 사용하는 방법
"""

from realtime_price_monitor import PriceMonitor

# 기본 사용 (비트코인, 5분 간격)
monitor = PriceMonitor(market='KRW-BTC', interval=30)  # 300초 = 5분
monitor.monitor()

# 다른 코인 모니터링
# monitor = PriceMonitor(market='KRW-ETH', interval=300)  # 이더리움
# monitor.monitor()

# 다른 간격으로 모니터링
# monitor = PriceMonitor(market='KRW-BTC', interval=60)   # 1분 간격
# monitor.monitor()

