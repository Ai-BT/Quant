"""
Upbit API 어댑터
실제 Upbit API와 통신
"""
import hashlib
import hmac
import jwt
import requests
import time
from typing import Dict, Any, List, Optional
from urllib.parse import urlencode

from app.adapters.upbit.exceptions import (
    UpbitError,
    UpbitAuthError,
    UpbitRateLimitError,
    UpbitAPIError,
)
from app.core.logging import get_logger

logger = get_logger(__name__, "system")


class UpbitAdapter:
    """Upbit API 어댑터"""
    
    BASE_URL = "https://api.upbit.com/v1"
    
    def __init__(self, access_key: str, secret_key: str):
        """
        Args:
            access_key: Upbit Access Key
            secret_key: Upbit Secret Key
        """
        self.access_key = access_key
        self.secret_key = secret_key
        self.last_request_time = 0
        self.min_request_interval = 0.1  # Rate limit: 최소 0.1초 간격
        
    def _wait_for_rate_limit(self):
        """Rate limit 대기"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()
    
    def _get_headers(self, query_string: Optional[str] = None) -> Dict[str, str]:
        """
        JWT 토큰 생성 및 헤더 반환
        
        Args:
            query_string: 쿼리 문자열 (선택사항)
            
        Returns:
            헤더 딕셔너리
        """
        payload = {
            "access_key": self.access_key,
            "nonce": str(int(time.time() * 1000)),
        }
        
        if query_string:
            payload["query_string"] = query_string
        
        jwt_token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        authorization_token = f"Bearer {jwt_token}"
        
        return {
            "Authorization": authorization_token,
            "Content-Type": "application/json",
        }
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        is_private: bool = False,
    ) -> Dict[str, Any]:
        """
        API 요청
        
        Args:
            method: HTTP 메서드 (GET, POST, DELETE)
            endpoint: API 엔드포인트
            params: 요청 파라미터
            is_private: Private API 여부
            
        Returns:
            응답 데이터
            
        Raises:
            UpbitError: API 오류
        """
        self._wait_for_rate_limit()
        
        url = f"{self.BASE_URL}/{endpoint}"
        headers = {"Accept": "application/json"}
        
        if is_private:
            query_string = urlencode(params) if params else ""
            headers.update(self._get_headers(query_string))
        
        try:
            if method == "GET":
                response = requests.get(url, params=params, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=params, headers=headers, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, params=params, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise UpbitAuthError("인증 실패. API 키를 확인하세요.")
            elif response.status_code == 429:
                raise UpbitRateLimitError("Rate limit 초과. 잠시 후 다시 시도하세요.")
            else:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get("error", {}).get("message", str(e))
                raise UpbitAPIError(f"API 오류: {error_msg}", error_code=response.status_code)
        except requests.exceptions.RequestException as e:
            raise UpbitError(f"요청 실패: {str(e)}")
    
    # 계좌 조회
    def get_accounts(self) -> List[Dict[str, Any]]:
        """전체 계좌 조회"""
        try:
            response = self._request("GET", "accounts", is_private=True)
            return response
        except Exception as e:
            logger.error(f"계좌 조회 실패: {e}")
            raise
    
    def get_balance(self, currency: str = "KRW") -> Dict[str, Any]:
        """
        특정 화폐 잔고 조회
        
        Args:
            currency: 화폐 코드 (KRW, BTC, ETH 등)
            
        Returns:
            잔고 정보
        """
        accounts = self.get_accounts()
        for account in accounts:
            if account["currency"] == currency:
                return account
        return {
            "currency": currency,
            "balance": "0.0",
            "locked": "0.0",
            "avg_buy_price": "0.0",
            "avg_buy_price_modified": False,
            "unit_currency": "KRW",
        }
    
    # 주문
    def place_order(
        self,
        market: str,
        side: str,
        volume: Optional[float] = None,
        price: Optional[float] = None,
        ord_type: str = "limit",
    ) -> Dict[str, Any]:
        """
        주문하기
        
        Args:
            market: 마켓 코드 (KRW-BTC 등)
            side: 주문 종류 (bid: 매수, ask: 매도)
            volume: 주문 수량
            price: 주문 가격
            ord_type: 주문 타입 (limit, price, market)
            
        Returns:
            주문 결과
        """
        params = {
            "market": market,
            "side": side,
            "ord_type": ord_type,
        }
        
        if ord_type == "limit":
            if volume and price:
                params["volume"] = str(volume)
                params["price"] = str(price)
            else:
                raise ValueError("limit 주문은 volume과 price가 필요합니다.")
        elif ord_type == "price":
            if price:
                params["price"] = str(price)
            else:
                raise ValueError("price 주문은 price가 필요합니다.")
        elif ord_type == "market":
            if side == "bid" and price:
                params["price"] = str(price)
            elif side == "ask" and volume:
                params["volume"] = str(volume)
            else:
                raise ValueError("market 주문 파라미터가 올바르지 않습니다.")
        
        try:
            response = self._request("POST", "orders", params=params, is_private=True)
            return response
        except Exception as e:
            logger.error(f"주문 실패: {e}")
            raise
    
    def cancel_order(self, uuid: str) -> Dict[str, Any]:
        """
        주문 취소
        
        Args:
            uuid: 주문 UUID
            
        Returns:
            취소 결과
        """
        params = {"uuid": uuid}
        try:
            response = self._request("DELETE", "order", params=params, is_private=True)
            return response
        except Exception as e:
            logger.error(f"주문 취소 실패: {e}")
            raise
    
    def get_orders(self, market: Optional[str] = None, state: str = "wait") -> List[Dict[str, Any]]:
        """
        주문 조회
        
        Args:
            market: 마켓 코드 (선택사항)
            state: 주문 상태 (wait, done, cancel)
            
        Returns:
            주문 목록
        """
        params = {"state": state}
        if market:
            params["market"] = market
        
        try:
            response = self._request("GET", "orders", params=params, is_private=True)
            return response
        except Exception as e:
            logger.error(f"주문 조회 실패: {e}")
            raise
    
    # 시장 데이터
    def get_ticker(self, markets: List[str]) -> List[Dict[str, Any]]:
        """
        현재가 조회
        
        Args:
            markets: 마켓 코드 리스트
            
        Returns:
            현재가 정보
        """
        if not markets:
            return []
        
        # 마켓 코드를 배치로 나누어 요청 (한 번에 너무 많으면 실패할 수 있음)
        batch_size = 10
        all_tickers = []
        
        for i in range(0, len(markets), batch_size):
            batch = markets[i:i + batch_size]
            params = {"markets": ",".join(batch)}
            try:
                response = self._request("GET", "ticker", params=params, is_private=False)
                if isinstance(response, list):
                    all_tickers.extend(response)
                elif isinstance(response, dict) and "error" in response:
                    # 에러가 발생하면 개별 마켓으로 재시도
                    logger.debug(f"배치 조회 실패, 개별 마켓으로 재시도: {batch}")
                    # 개별 마켓으로 요청
                    for market in batch:
                        try:
                            individual_response = self._request("GET", "ticker", params={"markets": market}, is_private=False)
                            if isinstance(individual_response, list) and len(individual_response) > 0:
                                all_tickers.extend(individual_response)
                        except Exception:
                            # 개별 마켓도 실패하면 건너뛰기
                            continue
                else:
                    all_tickers.extend(response if isinstance(response, list) else [response])
            except UpbitAPIError as e:
                # "Code not found" 오류는 일부 마켓이 존재하지 않는 경우
                if "not found" in str(e).lower() or "code" in str(e).lower():
                    # 배치 실패 시 개별 마켓으로 재시도
                    logger.debug(f"배치 조회 실패 (Code not found), 개별 마켓으로 재시도: {batch}")
                    for market in batch:
                        try:
                            individual_response = self._request("GET", "ticker", params={"markets": market}, is_private=False)
                            if isinstance(individual_response, list) and len(individual_response) > 0:
                                all_tickers.extend(individual_response)
                        except Exception:
                            # 개별 마켓도 실패하면 건너뛰기
                            continue
                else:
                    logger.error(f"현재가 조회 실패: {e}")
                    # 다른 에러도 개별 마켓으로 재시도
                    for market in batch:
                        try:
                            individual_response = self._request("GET", "ticker", params={"markets": market}, is_private=False)
                            if isinstance(individual_response, list) and len(individual_response) > 0:
                                all_tickers.extend(individual_response)
                        except Exception:
                            continue
            except Exception as e:
                # 예외 발생 시 개별 마켓으로 재시도
                logger.debug(f"배치 조회 예외 발생, 개별 마켓으로 재시도: {batch}, {e}")
                for market in batch:
                    try:
                        individual_response = self._request("GET", "ticker", params={"markets": market}, is_private=False)
                        if isinstance(individual_response, list) and len(individual_response) > 0:
                            all_tickers.extend(individual_response)
                    except Exception:
                        continue
        
        return all_tickers
    
    def get_ohlcv(
        self,
        market: str,
        interval: str = "day",
        count: int = 200,
        to: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        OHLCV 조회
        
        Args:
            market: 마켓 코드
            interval: 캔들 간격 (day, minute1, minute3, minute5, ...)
            count: 조회 개수
            to: 조회 시점 (선택사항)
            
        Returns:
            OHLCV 데이터
        """
        params = {
            "market": market,
            "interval": interval,
            "count": count,
        }
        if to:
            params["to"] = to
        
        try:
            response = self._request("GET", f"candles/{interval}", params=params, is_private=False)
            return response
        except Exception as e:
            logger.error(f"OHLCV 조회 실패: {e}")
            raise

