"""
작업 상태 저장 및 재개 가능 구조
"""
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from app.core.logging import get_logger

logger = get_logger(__name__, "system")


class JobStateManager:
    """작업 상태 관리자"""
    
    def __init__(self, state_dir: Path = Path("state")):
        self.state_dir = state_dir
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.job_states: Dict[str, Dict[str, Any]] = {}
        self._load_states()
    
    def _get_state_file(self, job_id: str) -> Path:
        """작업 상태 파일 경로"""
        return self.state_dir / f"{job_id}.json"
    
    def _load_states(self):
        """저장된 상태 로드"""
        try:
            for state_file in self.state_dir.glob("*.json"):
                job_id = state_file.stem
                try:
                    with open(state_file, "r", encoding="utf-8") as f:
                        self.job_states[job_id] = json.load(f)
                except Exception as e:
                    logger.warning(f"Failed to load state file {state_file}: {e}")
        except Exception as e:
            logger.warning(f"Failed to load states: {e}")
    
    def save_state(self, job_id: str, state: Dict[str, Any]):
        """작업 상태 저장"""
        try:
            state["updated_at"] = datetime.now().isoformat()
            self.job_states[job_id] = state
            
            # 파일에 저장
            state_file = self._get_state_file(job_id)
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Job state saved: {job_id}")
        except Exception as e:
            logger.error(f"Failed to save job state {job_id}: {e}")
    
    def get_state(self, job_id: str) -> Optional[Dict[str, Any]]:
        """작업 상태 조회"""
        return self.job_states.get(job_id)
    
    def update_state(self, job_id: str, updates: Dict[str, Any]):
        """작업 상태 업데이트"""
        if job_id not in self.job_states:
            self.job_states[job_id] = {
                "job_id": job_id,
                "status": "pending",
                "created_at": datetime.now().isoformat(),
            }
        
        self.job_states[job_id].update(updates)
        self.save_state(job_id, self.job_states[job_id])
    
    def delete_state(self, job_id: str):
        """작업 상태 삭제"""
        if job_id in self.job_states:
            del self.job_states[job_id]
        
        state_file = self._get_state_file(job_id)
        if state_file.exists():
            try:
                state_file.unlink()
                logger.debug(f"Job state deleted: {job_id}")
            except Exception as e:
                logger.warning(f"Failed to delete state file {state_file}: {e}")
    
    def get_all_states(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """모든 작업 상태 조회"""
        states = list(self.job_states.values())
        if status:
            states = [s for s in states if s.get("status") == status]
        return states
    
    def resume_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """작업 재개"""
        state = self.get_state(job_id)
        if not state:
            logger.warning(f"Job {job_id} state not found")
            return None
        
        if state.get("status") not in ["paused", "failed"]:
            logger.warning(f"Job {job_id} cannot be resumed from status {state.get('status')}")
            return None
        
        logger.info(f"Resuming job {job_id}")
        self.update_state(job_id, {
            "status": "running",
            "resumed_at": datetime.now().isoformat(),
        })
        
        return self.get_state(job_id)


# 전역 작업 상태 관리자 인스턴스
job_state_manager = JobStateManager()


