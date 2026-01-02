from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from pathlib import Path
import os
from dotenv import load_dotenv


# 프로젝트 루트 경로 계산
# app/core/config.py -> app/core -> app -> backend
BACKEND_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = BACKEND_ROOT / ".env"

# .env 파일 직접 로드 (pydantic-settings가 읽지 못할 경우 대비)
if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE, override=True)
    # 디버깅: 로드된 환경 변수 확인
    import os
    if os.getenv('UPBIT_ACCESS_KEY'):
        print(f"✅ Upbit API 키 로드됨: {os.getenv('UPBIT_ACCESS_KEY')[:10]}...")
    else:
        print(f"⚠️ Upbit API 키가 로드되지 않았습니다. ENV_FILE: {ENV_FILE}")


class Settings(BaseSettings):
    # App
    app_name: str = "Quant Trading System"
    debug: bool = False
    api_version: str = "v1"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    
    # Upbit API
    upbit_access_key: str = ""
    upbit_secret_key: str = ""
    upbit_server_url: str = "https://api.upbit.com"
    
    @property
    def has_upbit_credentials(self) -> bool:
        """Upbit API 키가 설정되어 있는지 확인"""
        return bool(self.upbit_access_key and self.upbit_secret_key)
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) if ENV_FILE.exists() else None,
        case_sensitive=False,
        env_ignore_empty=True,
        # 환경 변수 이름 매핑 (대문자 -> 소문자_언더스코어)
        env_prefix="",
    )


settings = Settings()

