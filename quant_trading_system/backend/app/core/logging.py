"""
로깅 시스템 설정
파일 로그 및 DB 로그 기록
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional
from app.core.mock_data import mock_store


class DatabaseLogHandler(logging.Handler):
    """DB에 로그를 기록하는 커스텀 핸들러"""
    
    def emit(self, record):
        """로그 레코드를 DB에 저장"""
        try:
            log_entry = {
                "level": record.levelname,
                "type": getattr(record, "log_type", "system"),
                "message": record.getMessage(),
                "details": {
                    "module": record.module,
                    "funcName": record.funcName,
                    "lineno": record.lineno,
                    "pathname": record.pathname,
                },
                "created_at": datetime.fromtimestamp(record.created).isoformat(),
            }
            mock_store.add_log(
                level=log_entry["level"],
                log_type=log_entry["type"],
                message=log_entry["message"],
                details=log_entry["details"],
            )
        except Exception:
            # DB 로그 실패 시 무시 (무한 루프 방지)
            pass


def setup_logging(
    log_dir: Path = Path("logs"),
    log_file: str = "app.log",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    level: int = logging.INFO,
) -> logging.Logger:
    """
    로깅 시스템 설정
    
    Args:
        log_dir: 로그 파일 디렉토리
        log_file: 로그 파일명
        max_bytes: 로그 파일 최대 크기
        backup_count: 백업 파일 개수
        level: 로그 레벨
        
    Returns:
        설정된 로거
    """
    # 로그 디렉토리 생성
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / log_file
    
    # 루트 로거 설정
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # 기존 핸들러 제거
    logger.handlers.clear()
    
    # 포맷터 설정
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 파일 핸들러 (로테이션)
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # DB 핸들러
    db_handler = DatabaseLogHandler()
    db_handler.setLevel(level)
    db_handler.setFormatter(formatter)
    logger.addHandler(db_handler)
    
    return logger


def get_logger(name: str, log_type: str = "system") -> logging.Logger:
    """
    특정 이름의 로거 가져오기
    
    Args:
        name: 로거 이름
        log_type: 로그 타입 (system, strategy, order)
        
    Returns:
        로거 인스턴스
    """
    logger = logging.getLogger(name)
    
    # 로그 타입을 레코드에 추가하기 위한 어댑터
    class LogTypeAdapter(logging.LoggerAdapter):
        def process(self, msg, kwargs):
            kwargs.setdefault("extra", {})["log_type"] = self.extra["log_type"]
            return msg, kwargs
    
    return LogTypeAdapter(logger, {"log_type": log_type})


# 전역 로거 설정
app_logger = setup_logging()


