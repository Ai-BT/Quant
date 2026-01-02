"""
환경 변수 디버깅 스크립트
"""
import sys
from pathlib import Path
import os
from dotenv import load_dotenv

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "backend"))

# .env 파일 직접 로드
env_file = project_root / "backend" / ".env"
print(f"ENV_FILE 경로: {env_file}")
print(f"ENV_FILE 존재 여부: {env_file.exists()}")

if env_file.exists():
    print(f"\n.env 파일 내용:")
    print("=" * 50)
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
        print(content)
    print("=" * 50)
    
    # dotenv로 로드
    load_dotenv(dotenv_path=env_file, override=True)
    print("\ndotenv 로드 후 환경 변수:")
    print(f"  UPBIT_ACCESS_KEY: {os.getenv('UPBIT_ACCESS_KEY', '없음')}")
    print(f"  UPBIT_SECRET_KEY: {os.getenv('UPBIT_SECRET_KEY', '없음')}")
    print(f"  UPBIT_SERVER_URL: {os.getenv('UPBIT_SERVER_URL', '없음')}")
    
    # pydantic-settings로 로드
    print("\npydantic-settings로 로드:")
    from app.core.config import settings
    print(f"  upbit_access_key: {settings.upbit_access_key or '없음'}")
    print(f"  upbit_secret_key: {settings.upbit_secret_key or '없음'}")
    print(f"  upbit_server_url: {settings.upbit_server_url}")
    print(f"  has_upbit_credentials: {settings.has_upbit_credentials}")
else:
    print("❌ .env 파일이 없습니다!")


