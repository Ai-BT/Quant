"""
FastAPI 메인 애플리케이션
python -m app.api.main 실행 시 호출됨
"""
import uvicorn
from fastapi import FastAPI

app = FastAPI(
    title="QuantBot API",
    description="24시간 코인 자동매매 시스템 API",
    version="0.1.0"
)


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "QuantBot API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}


if __name__ == "__main__":
    # 환경 변수에서 설정 읽기 (기본값 사용)
    import os
    from pathlib import Path
    
    try:
        from dotenv import load_dotenv
        # 프로젝트 루트에서 .env 파일 로드
        project_root = Path(__file__).parent.parent.parent
        load_dotenv(project_root / ".env")
    except ImportError:
        # dotenv가 없으면 환경 변수 직접 사용
        pass
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    print(f"QuantBot API 서버 시작: http://{host}:{port}")
    print(f"API 문서: http://{host}:{port}/docs")
    
    uvicorn.run(
        "app.api.main:app",
        host=host,
        port=port,
        reload=True  # 개발 모드
    )

