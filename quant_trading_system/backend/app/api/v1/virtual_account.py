"""
가상 계좌 API

가상 자금으로 전략을 테스트하기 위한 계좌 관리 API
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any, List
from app.core.virtual_account_manager import virtual_account_manager
from app.core.logging import get_logger

# get_upbit_adapter는 upbit.py에 있으므로 여기서는 직접 adapter를 생성
from app.adapters.upbit.adapter import UpbitAdapter
from app.core.config import settings
from app.adapters.upbit.exceptions import UpbitAuthError, UpbitError

logger = get_logger(__name__, "virtual_account")
router = APIRouter(prefix="/virtual-account", tags=["Virtual Account"])


@router.get("/balance")
async def get_balance(strategy_id: Optional[str] = Query(None, description="전략 ID (없으면 전체 합계)")):
    """
    가상 계좌 잔고 조회
    
    strategy_id가 없으면 모든 전략 계좌의 합계를 반환
    """
    try:
        if strategy_id:
            # 특정 전략 계좌 조회
            account = virtual_account_manager.get_account(strategy_id)
            balance = account.get_balance()
            holdings = account.get_holdings()
        else:
            # 모든 전략 계좌 합계
            all_accounts = virtual_account_manager.get_all_accounts()
            if not all_accounts:
                # 전략 계좌가 없으면 기본 계좌 사용
                account = virtual_account_manager.get_default_account()
                balance = account.get_balance()
                holdings = account.get_holdings()
            else:
                # 모든 전략 계좌 합산
                total_balance = 0
                total_holdings: Dict[str, float] = {}
                
                for acc in all_accounts.values():
                    total_balance += acc.get_balance()
                    acc_holdings = acc.get_holdings()
                    for currency, quantity in acc_holdings.items():
                        total_holdings[currency] = total_holdings.get(currency, 0) + quantity
                
                balance = total_balance
                holdings = total_holdings
        
        # 현재가 조회 (보유 코인이 있는 경우)
        prices = {}
        if holdings:
            try:
                # UpbitAdapter 인스턴스 생성
                if settings.upbit_access_key and settings.upbit_secret_key:
                    adapter = UpbitAdapter(
                        access_key=settings.upbit_access_key,
                        secret_key=settings.upbit_secret_key
                    )
                    markets = [f"KRW-{currency}" for currency in holdings.keys()]
                    tickers = adapter.get_ticker(markets)
                    for ticker in tickers:
                        if ticker and ticker.get('market'):
                            currency = ticker['market'].replace('KRW-', '')
                            prices[currency] = ticker.get('trade_price', 0)
            except Exception as e:
                logger.warning(f"현재가 조회 실패: {e}")
        
        if strategy_id:
            account = virtual_account_manager.get_account(strategy_id)
            total_value = account.get_total_value(prices)
            summary = account.get_summary(prices)
        else:
            # 모든 계좌 합계
            if all_accounts:
                total_value = sum(acc.get_total_value(prices) for acc in all_accounts.values())
                
                # 합계 summary 계산
                initial_balance = virtual_account_manager.initial_balance_per_strategy * len(all_accounts)
                profit_loss = total_value - initial_balance
                profit_loss_rate = (profit_loss / initial_balance * 100) if initial_balance > 0 else 0
                
                summary = {
                    'initial_balance': initial_balance,
                    'current_balance': balance,
                    'total_value': total_value,
                    'profit_loss': profit_loss,
                    'profit_loss_rate': profit_loss_rate,
                }
            else:
                account = virtual_account_manager.get_default_account()
                total_value = account.get_total_value(prices)
                summary = account.get_summary(prices)
        
        # 평균 매수가 정보 추가
        avg_buy_prices = {}
        if strategy_id:
            account = virtual_account_manager.get_account(strategy_id)
            avg_buy_prices = account.get_avg_buy_prices()
        else:
            # 전체 합계의 경우 각 계좌의 평균 매수가를 계산할 수 없으므로 빈 딕셔너리
            # (실제로는 여러 전략이 같은 코인을 보유할 수 있어서 평균 매수가를 계산하기 어려움)
            pass
        
        return {
            "success": True,
            "data": {
                "balance": balance,
                "holdings": holdings,
                "avg_buy_prices": avg_buy_prices,
                "prices": prices,
                "total_value": total_value,
                "summary": summary,
                "strategy_id": strategy_id,
            }
        }
    except Exception as e:
        logger.error(f"가상 계좌 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"가상 계좌 조회 실패: {str(e)}")


@router.get("/summary")
async def get_summary(strategy_id: Optional[str] = Query(None, description="전략 ID (없으면 전체 합계)")):
    """가상 계좌 요약 정보"""
    try:
        if strategy_id:
            account = virtual_account_manager.get_account(strategy_id)
            holdings = account.get_holdings()
        else:
            all_accounts = virtual_account_manager.get_all_accounts()
            if not all_accounts:
                account = virtual_account_manager.get_default_account()
                holdings = account.get_holdings()
            else:
                total_holdings: Dict[str, float] = {}
                for acc in all_accounts.values():
                    acc_holdings = acc.get_holdings()
                    for currency, quantity in acc_holdings.items():
                        total_holdings[currency] = total_holdings.get(currency, 0) + quantity
                holdings = total_holdings
        
        # 현재가 조회
        prices = {}
        if holdings:
            try:
                # UpbitAdapter 인스턴스 생성
                if settings.upbit_access_key and settings.upbit_secret_key:
                    adapter = UpbitAdapter(
                        access_key=settings.upbit_access_key,
                        secret_key=settings.upbit_secret_key
                    )
                    markets = [f"KRW-{currency}" for currency in holdings.keys()]
                    tickers = adapter.get_ticker(markets)
                    for ticker in tickers:
                        if ticker and ticker.get('market'):
                            currency = ticker['market'].replace('KRW-', '')
                            prices[currency] = ticker.get('trade_price', 0)
            except Exception as e:
                logger.warning(f"현재가 조회 실패: {e}")
        
        if strategy_id:
            account = virtual_account_manager.get_account(strategy_id)
            summary = account.get_summary(prices)
        else:
            # 모든 계좌 합계
            all_accounts = virtual_account_manager.get_all_accounts()
            if all_accounts:
                total_value = sum(acc.get_total_value(prices) for acc in all_accounts.values())
                total_balance = sum(acc.get_balance() for acc in all_accounts.values())
                initial_balance = virtual_account_manager.initial_balance_per_strategy * len(all_accounts)
                profit_loss = total_value - initial_balance
                profit_loss_rate = (profit_loss / initial_balance * 100) if initial_balance > 0 else 0
                
                summary = {
                    'initial_balance': initial_balance,
                    'current_balance': total_balance,
                    'total_value': total_value,
                    'profit_loss': profit_loss,
                    'profit_loss_rate': profit_loss_rate,
                }
            else:
                account = virtual_account_manager.get_default_account()
                summary = account.get_summary(prices)
        
        return {
            "success": True,
            "data": summary
        }
    except Exception as e:
        logger.error(f"가상 계좌 요약 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"가상 계좌 요약 조회 실패: {str(e)}")


@router.get("/trades")
async def get_trades(
    limit: Optional[int] = Query(50, description="조회할 거래 개수"),
    strategy_id: Optional[str] = Query(None, description="전략 ID (없으면 모든 전략의 거래 내역)")
):
    """거래 내역 조회"""
    try:
        if strategy_id:
            # 특정 전략의 거래 내역
            account = virtual_account_manager.get_account(strategy_id)
            history = account.get_trade_history(limit=limit)
        else:
            # 모든 전략의 거래 내역 합쳐서 정렬
            all_accounts = virtual_account_manager.get_all_accounts()
            all_trades = []
            
            for sid, acc in all_accounts.items():
                trades = acc.get_trade_history(limit=1000)  # 충분히 많이 가져오기
                for trade in trades:
                    trade_copy = trade.copy()
                    trade_copy['strategy_id'] = sid  # 전략 ID 추가
                    all_trades.append(trade_copy)
            
            # 타임스탬프 기준으로 정렬 (최신순)
            all_trades.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            history = all_trades[:limit]
        
        return {
            "success": True,
            "data": history
        }
    except Exception as e:
        logger.error(f"거래 내역 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"거래 내역 조회 실패: {str(e)}")


@router.get("/strategies")
async def get_strategy_accounts():
    """모든 전략 계좌 목록 조회"""
    try:
        all_accounts = virtual_account_manager.get_all_accounts()
        
        # UpbitAdapter 생성 (현재가 조회용)
        prices_map = {}
        if settings.upbit_access_key and settings.upbit_secret_key:
            try:
                adapter = UpbitAdapter(
                    access_key=settings.upbit_access_key,
                    secret_key=settings.upbit_secret_key
                )
                
                # 모든 전략의 보유 코인 수집
                all_currencies = set()
                for acc in all_accounts.values():
                    holdings = acc.get_holdings()
                    all_currencies.update(holdings.keys())
                
                if all_currencies:
                    markets = [f"KRW-{currency}" for currency in all_currencies]
                    tickers = adapter.get_ticker(markets)
                    for ticker in tickers:
                        if ticker and ticker.get('market'):
                            currency = ticker['market'].replace('KRW-', '')
                            prices_map[currency] = ticker.get('trade_price', 0)
            except Exception as e:
                logger.warning(f"현재가 조회 실패: {e}")
        
        result = []
        for strategy_id, account in all_accounts.items():
            holdings = account.get_holdings()
            avg_buy_prices = account.get_avg_buy_prices()
            prices = {curr: prices_map.get(curr, 0) for curr in holdings.keys()}
            total_value = account.get_total_value(prices)
            summary = account.get_summary(prices)
            # summary에 prices 추가
            summary['prices'] = prices
            
            result.append({
                'strategy_id': strategy_id,
                'balance': account.get_balance(),
                'holdings': holdings,
                'avg_buy_prices': avg_buy_prices,
                'total_value': total_value,
                'summary': summary,
                'prices': prices,  # 직접 접근을 위해 추가
                'trade_count': len(account.get_trade_history(limit=10000)),
            })
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"전략 계좌 목록 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"전략 계좌 목록 조회 실패: {str(e)}")


@router.post("/reset")
async def reset_account(strategy_id: Optional[str] = Query(None, description="전략 ID (없으면 모든 계좌 초기화)")):
    """가상 계좌 초기화"""
    try:
        if strategy_id:
            # 특정 전략 계좌 초기화
            account = virtual_account_manager.get_account(strategy_id)
            account.reset()
            logger.info(f"전략 계좌 초기화: {strategy_id}")
        else:
            # 모든 전략 계좌 초기화
            all_accounts = virtual_account_manager.get_all_accounts()
            for sid, account in all_accounts.items():
                account.reset()
                logger.info(f"전략 계좌 초기화: {sid}")
            
            # 기본 계좌도 초기화
            default_account = virtual_account_manager.get_default_account()
            default_account.reset()
        
        return {
            "success": True,
            "message": f"가상 계좌가 초기화되었습니다. (strategy_id: {strategy_id or 'all'})"
        }
    except Exception as e:
        logger.error(f"가상 계좌 초기화 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"가상 계좌 초기화 실패: {str(e)}")

