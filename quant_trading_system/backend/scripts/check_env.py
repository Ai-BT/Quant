"""
환경 변수 확인 스크립트
"""
import sys
from pathlib import Path
from dotenv import load_dotenv

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent.parent
backend_dir = project_root / "backend"
sys.path.insert(0, str(backend_dir))

# .env 파일 직접 로드 (config.py가 로드되기 전에)
env_file = backend_dir / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file, override=True)

from app.core.config import settings

print("=" * 50)
print("환경 변수 확인")
print("=" * 50)
print(f"ENV_FILE 경로: {env_file}")
print(f"ENV_FILE 존재 여부: {env_file.exists()}")
print()
print("Upbit API 설정:")
print(f"  UPBIT_ACCESS_KEY: {'✅ 설정됨' if settings.upbit_access_key else '❌ 없음'}")
if settings.upbit_access_key:
    print(f"    값: {settings.upbit_access_key[:10]}...")
print(f"  UPBIT_SECRET_KEY: {'✅ 설정됨' if settings.upbit_secret_key else '❌ 없음'}")
if settings.upbit_secret_key:
    print(f"    값: {settings.upbit_secret_key[:10]}...")
print(f"  UPBIT_SERVER_URL: {settings.upbit_server_url}")
print()
print(f"has_upbit_credentials: {settings.has_upbit_credentials}")

