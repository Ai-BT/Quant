"""
Upbit API 연동 엔드포인트
실제 계좌 조회 및 주문
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from app.core.config import settings, ENV_FILE
from app.adapters.upbit.adapter import UpbitAdapter
from app.adapters.upbit.exceptions import UpbitError, UpbitAuthError
from app.core.logging import get_logger

logger = get_logger(__name__, "system")
router = APIRouter(prefix="/upbit", tags=["Upbit"])


def get_upbit_adapter() -> UpbitAdapter:
    """UpbitAdapter 인스턴스 생성"""
    # 환경 변수 직접 확인 (설정이 제대로 로드되지 않았을 경우 대비)
    import os
    from dotenv import load_dotenv
    from pathlib import Path
    
    # 경로 직접 계산 (app/api/v1/upbit.py -> app/api/v1 -> app/api -> app -> backend)
    backend_root = Path(__file__).parent.parent.parent.parent
    env_file = backend_root / ".env"
    
    # .env 파일 다시 로드 시도
    if env_file.exists():
        load_dotenv(dotenv_path=env_file, override=True)
        logger.debug(f"✅ .env 파일 로드됨: {env_file}")
    else:
        logger.warning(f"⚠️ .env 파일을 찾을 수 없습니다: {env_file}")
    
    # settings에서 먼저 확인, 없으면 환경 변수에서 직접 가져오기
    access_key = settings.upbit_access_key or os.getenv('UPBIT_ACCESS_KEY', '')
    secret_key = settings.upbit_secret_key or os.getenv('UPBIT_SECRET_KEY', '')
    
    if not access_key or not secret_key:
        logger.error(
            f"Upbit API 키가 설정되지 않았습니다. "
            f"settings.access_key: {'설정됨' if settings.upbit_access_key else '없음'}, "
            f"settings.secret_key: {'설정됨' if settings.upbit_secret_key else '없음'}, "
            f"env.UPBIT_ACCESS_KEY: {'설정됨' if os.getenv('UPBIT_ACCESS_KEY') else '없음'}, "
            f"env_file: {env_file}, exists: {env_file.exists()}"
        )
        raise HTTPException(
            status_code=500,
            detail="Upbit API 키가 설정되지 않았습니다. backend/.env 파일을 생성하고 UPBIT_ACCESS_KEY와 UPBIT_SECRET_KEY를 설정한 후 서버를 재시작하세요."
        )
    
    # 환경 변수에서 직접 가져온 값 사용
    return UpbitAdapter(access_key, secret_key)


@router.get("/accounts")
async def get_accounts(adapter: UpbitAdapter = Depends(get_upbit_adapter)):
    """전체 계좌 조회"""
    try:
        accounts = adapter.get_accounts()
        return {
            "success": True,
            "data": accounts,
            "count": len(accounts),
        }
    except UpbitAuthError as e:
        logger.error(f"Upbit 인증 오류: {e}")
        raise HTTPException(status_code=401, detail=str(e))
    except UpbitError as e:
        logger.error(f"Upbit API 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"계좌 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"계좌 조회 실패: {str(e)}")


@router.get("/balance/{currency}")
async def get_balance(currency: str, adapter: UpbitAdapter = Depends(get_upbit_adapter)):
    """특정 화폐 잔고 조회"""
    try:
        balance = adapter.get_balance(currency)
        return {
            "success": True,
            "data": balance,
        }
    except UpbitAuthError as e:
        logger.error(f"Upbit 인증 오류: {e}")
        raise HTTPException(status_code=401, detail=str(e))
    except UpbitError as e:
        logger.error(f"Upbit API 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"잔고 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"잔고 조회 실패: {str(e)}")


@router.get("/ticker")
async def get_ticker(markets: str, adapter: UpbitAdapter = Depends(get_upbit_adapter)):
    """현재가 조회
    
    Args:
        markets: 마켓 코드 (쉼표로 구분, 예: KRW-BTC,KRW-ETH)
    """
    try:
        market_list = [m.strip() for m in markets.split(",") if m.strip()]
        if not market_list:
            return {
                "success": True,
                "data": [],
                "message": "마켓 코드가 없습니다.",
            }
        
        tickers = adapter.get_ticker(market_list)
        return {
            "success": True,
            "data": tickers,
            "requested": len(market_list),
            "received": len(tickers),
        }
    except UpbitError as e:
        # 일부 마켓이 존재하지 않아도 빈 리스트 반환
        if "not found" in str(e).lower() or "code" in str(e).lower():
            logger.warning(f"일부 마켓이 존재하지 않습니다: {markets}")
            return {
                "success": True,
                "data": [],
                "message": "일부 마켓이 존재하지 않거나 상장폐지되었습니다.",
            }
        logger.error(f"현재가 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"현재가 조회 실패: {e}", exc_info=True)
        # 에러가 발생해도 빈 리스트 반환 (프론트엔드가 계속 작동하도록)
        return {
            "success": False,
            "data": [],
            "error": str(e),
        }


@router.get("/orders")
async def get_orders(
    market: str = None,
    state: str = "wait",
    adapter: UpbitAdapter = Depends(get_upbit_adapter),
):
    """주문 조회
    
    Args:
        market: 마켓 코드 (선택사항)
        state: 주문 상태 (wait, done, cancel)
    """
    try:
        orders = adapter.get_orders(market=market, state=state)
        return {
            "success": True,
            "data": orders,
            "count": len(orders),
        }
    except UpbitAuthError as e:
        logger.error(f"Upbit 인증 오류: {e}")
        raise HTTPException(status_code=401, detail=str(e))
    except UpbitError as e:
        logger.error(f"주문 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"주문 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"주문 조회 실패: {str(e)}")

