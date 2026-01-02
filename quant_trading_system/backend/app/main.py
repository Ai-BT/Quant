"""
FastAPI 애플리케이션 진입점
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.strategy_manager import strategy_manager
from app.core.exception_handler import (
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.api.v1 import health, strategies, positions, trades, logs, monitoring, upbit, virtual_account
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # 시작 시
    logger = setup_logging()
    logger.info("Application starting up...")
    
    # 백그라운드 작업 시작
    async def monitor_strategies():
        """전략 모니터링 백그라운드 작업"""
        while True:
            try:
                strategy_manager.check_all_strategies()
                await asyncio.sleep(60)  # 1분마다 체크
            except Exception as e:
                logger.error(f"Error in strategy monitoring: {e}", exc_info=True)
                await asyncio.sleep(60)
    
    # 백그라운드 태스크 시작
    monitor_task = asyncio.create_task(monitor_strategies())
    
    yield
    
    # 종료 시
    logger.info("Application shutting down...")
    monitor_task.cancel()
    try:
        await monitor_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title=settings.app_name,
    description="24시간 무중단 퀀트 트레이딩 시스템",
    version=settings.api_version,
    debug=settings.debug,
    lifespan=lifespan,
)

# 전역 예외 핸들러 등록
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(health.router, prefix=f"/api/{settings.api_version}")
app.include_router(strategies.router, prefix=f"/api/{settings.api_version}")
app.include_router(positions.router, prefix=f"/api/{settings.api_version}")
app.include_router(trades.router, prefix=f"/api/{settings.api_version}")
app.include_router(logs.router, prefix=f"/api/{settings.api_version}")
app.include_router(monitoring.router, prefix=f"/api/{settings.api_version}")
app.include_router(upbit.router, prefix=f"/api/{settings.api_version}")
app.include_router(virtual_account.router, prefix=f"/api/{settings.api_version}")


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Quant Trading System API",
        "version": settings.api_version,
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )

