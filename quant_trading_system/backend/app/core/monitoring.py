"""
프로세스 상태 모니터링
메모리, CPU, 디스크 사용량 등 모니터링
"""
import platform
from datetime import datetime
from typing import Dict, Any, Optional

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

from app.core.logging import get_logger

logger = get_logger(__name__, "system")


class SystemMonitor:
    """시스템 모니터링 클래스"""
    
    def __init__(self):
        self.start_time = datetime.now()
        if PSUTIL_AVAILABLE:
            self.process = psutil.Process()
        else:
            self.process = None
            logger.warning("psutil not available, system monitoring will be limited")
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """CPU 정보"""
        if not PSUTIL_AVAILABLE:
            return {"error": "psutil not available"}
        try:
            return {
                "usage_percent": psutil.cpu_percent(interval=0.1),
                "count": psutil.cpu_count(),
                "count_logical": psutil.cpu_count(logical=True),
            }
        except Exception as e:
            logger.warning(f"CPU 정보 조회 실패: {e}")
            return {"error": str(e)}
    
    def get_memory_info(self) -> Dict[str, Any]:
        """메모리 정보"""
        if not PSUTIL_AVAILABLE or not self.process:
            return {"error": "psutil not available"}
        try:
            process_memory = self.process.memory_info()
            system_memory = psutil.virtual_memory()
            
            return {
                "process": {
                    "rss_mb": round(process_memory.rss / 1024 / 1024, 2),  # MB
                    "vms_mb": round(process_memory.vms / 1024 / 1024, 2),  # MB
                },
                "system": {
                    "total_gb": round(system_memory.total / 1024 / 1024 / 1024, 2),
                    "available_gb": round(system_memory.available / 1024 / 1024 / 1024, 2),
                    "used_gb": round(system_memory.used / 1024 / 1024 / 1024, 2),
                    "percent": system_memory.percent,
                },
            }
        except Exception as e:
            logger.warning(f"메모리 정보 조회 실패: {e}")
            return {"error": str(e)}
    
    def get_disk_info(self) -> Dict[str, Any]:
        """디스크 정보"""
        if not PSUTIL_AVAILABLE:
            return {"error": "psutil not available"}
        try:
            disk = psutil.disk_usage("/")
            return {
                "total_gb": round(disk.total / 1024 / 1024 / 1024, 2),
                "used_gb": round(disk.used / 1024 / 1024 / 1024, 2),
                "free_gb": round(disk.free / 1024 / 1024 / 1024, 2),
                "percent": disk.percent,
            }
        except Exception as e:
            logger.warning(f"디스크 정보 조회 실패: {e}")
            return {"error": str(e)}
    
    def get_process_info(self) -> Dict[str, Any]:
        """프로세스 정보"""
        if not PSUTIL_AVAILABLE or not self.process:
            return {"error": "psutil not available"}
        try:
            return {
                "pid": self.process.pid,
                "name": self.process.name(),
                "status": self.process.status(),
                "create_time": datetime.fromtimestamp(self.process.create_time()).isoformat(),
                "num_threads": self.process.num_threads(),
                "cpu_percent": self.process.cpu_percent(interval=0.1),
            }
        except Exception as e:
            logger.warning(f"프로세스 정보 조회 실패: {e}")
            return {"error": str(e)}
    
    def get_system_info(self) -> Dict[str, Any]:
        """시스템 정보"""
        return {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
        }
    
    def get_uptime(self) -> Dict[str, Any]:
        """업타임 정보"""
        uptime = datetime.now() - self.start_time
        return {
            "started_at": self.start_time.isoformat(),
            "uptime_seconds": int(uptime.total_seconds()),
            "uptime_days": uptime.days,
            "uptime_hours": uptime.seconds // 3600,
            "uptime_minutes": (uptime.seconds % 3600) // 60,
        }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """모든 메트릭 조회"""
        return {
            "system": self.get_system_info(),
            "uptime": self.get_uptime(),
            "cpu": self.get_cpu_info(),
            "memory": self.get_memory_info(),
            "disk": self.get_disk_info(),
            "process": self.get_process_info(),
        }


# 전역 모니터 인스턴스
system_monitor = SystemMonitor()

